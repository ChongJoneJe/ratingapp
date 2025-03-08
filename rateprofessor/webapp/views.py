from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import ModuleInstance, Professor, Rating
from .serializers import ModuleInstanceSerializer, RatingSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def home(request):
    return HttpResponse("Welcome to the Rate Professor App!")

# --- Registration Endpoint ---
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]  # open endpoint
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not all([username, email, password]):
            return Response({'error': 'Provide username, email, and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


# --- Login Endpoint ---
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid Credentials'},
                            status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Debug: log the received header
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        print("Logout view received HTTP_AUTHORIZATION:", auth_header)

        # Prefer using the token from request.auth (populated by TokenAuthentication)
        token = request.auth
        if token:
            token.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            # Fallback: try to get the token from the request body or query parameters
            token_value = request.data.get("token") or request.GET.get("token")
            print("Fallback token value from body/GET:", token_value)
            if token_value:
                try:
                    token = Token.objects.get(key=token_value)
                    token.delete()
                    return Response(status=status.HTTP_200_OK)
                except Token.DoesNotExist:
                    return Response({"error": "Token not found."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Authentication credentials were not provided."},
                                status=status.HTTP_400_BAD_REQUEST)


# --- List Module Instances Endpoint ---
class ModuleInstanceList(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        instances = ModuleInstance.objects.all()
        serializer = ModuleInstanceSerializer(instances, many=True)
        return Response(serializer.data)


# --- View Professor Ratings (Overall) ---
class ProfessorRatingsView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        professors = Professor.objects.all()
        response_data = []
        for prof in professors:
            ratings = Rating.objects.filter(professor=prof)
            if ratings.exists():
                avg_rating = round(sum(r.rating for r in ratings) / ratings.count())
                stars = "*" * avg_rating
            else:
                stars = "Unrated"
            response_data.append({
                'professor': f"{prof.name} ({prof.professor_id})",
                'rating': stars
            })
        return Response(response_data)


# --- Average Rating for Professor in a Specific Module ---
class AverageRatingForModule(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, professor_id, module_code):
        ratings = Rating.objects.filter(
            professor__professor_id=professor_id,
            module_instance__module__code=module_code
        )
        if ratings.exists():
            avg_rating = round(sum(r.rating for r in ratings) / ratings.count())
            stars = "*" * avg_rating
        else:
            stars = "Unrated"
        return Response({
            'professor': professor_id,
            'module': module_code,
            'average_rating': stars
        })


@method_decorator(csrf_exempt, name='dispatch')
class RateProfessor(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Debug: print the received Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        print("RateProfessor received HTTP_AUTHORIZATION:", auth_header)

        professor_id = request.data.get("professor_id")
        module_code = request.data.get("module_code")
        year = request.data.get("year")
        semester = request.data.get("semester")
        rating_value = request.data.get("rating")

        # Validate all fields are provided
        if not all([professor_id, module_code, year, semester, rating_value]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the module instance
        try:
            module_instance = ModuleInstance.objects.get(
                module__code=module_code, year=year, semester=semester
            )
        except ModuleInstance.DoesNotExist:
            return Response({"error": "Module instance not found."}, status=status.HTTP_404_NOT_FOUND)

        # Find the professor
        try:
            professor = Professor.objects.get(professor_id=professor_id)
        except Professor.DoesNotExist:
            return Response({"error": "Professor not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check professor teaches the module instance
        if not module_instance.professors.filter(professor_id=professor_id).exists():
            return Response({"error": "Professor does not teach this module instance."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate rating is an integer between 1 and 5
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                raise ValueError
        except ValueError:
            return Response({"error": "Rating must be an integer between 1 and 5."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check that the user hasn't already rated this professor for this module instance
        if Rating.objects.filter(user=request.user, module_instance=module_instance, professor=professor).exists():
            return Response({"error": "You have already rated this professor for this module instance."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create the rating
        rating_obj = Rating.objects.create(
            user=request.user,
            module_instance=module_instance,
            professor=professor,
            rating=rating_value
        )
        serializer = RatingSerializer(rating_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
