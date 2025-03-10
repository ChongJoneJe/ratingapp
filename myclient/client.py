import requests

BASE_URL = "https://sc23jjc.pythonanywhere.com/api/"
session = requests.Session()

def register():
    print("Register a New User")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    data = {"username": username, "email": email, "password": password}
    response = session.post(BASE_URL + "register/", json=data)
    if response.status_code == 201:
        token = response.json().get("token")
        print("Registration successful!")
        print("Your token:", token)
    else:
        error = response.json().get("error", "Unknown error")
        print("Registration failed:", error)

def login():
    print("User Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    data = {"username": username, "password": password}
    response = session.post(BASE_URL + "login/", json=data)
    if response.status_code == 200:
        token = response.json().get("token")
        session.headers.update({"Authorization": f"Token {token}"})
        print(f"Login successful!: {token}")
    else:
        error = response.json().get("error", "Unknown error")
        print("Login failed:", error)
        
def logout():
    token = session.headers.get("Authorization")
    if not token:
        print("No authentication token found. Please log in first.")
        return
    # print("Session headers before logout:", session.headers)
    token_request = token.split(" ")[1] 
    headers = {"Authorization": token}
    data = {"token": token_request}
    response = requests.post(BASE_URL + "logout/", headers=headers, json=data)
    if response.status_code == 200:
        session.cookies.clear()
        session.headers.pop("Authorization", None)
        print("Logged out successfully!")
    else:
        print("Logout failed:", response.json())

def list_module_instances():
    response = session.get(BASE_URL + "module-instances/")
    if response.status_code == 200:
        instances = response.json()
        if not instances:
            print("No module instances available.")
        for instance in instances:
            module = instance.get("module", {})
            code = module.get("code", "N/A")
            name = module.get("name", "N/A")
            year = instance.get("year", "N/A")
            semester = instance.get("semester", "N/A")
            profs = instance.get("professors", [])
            professors_str = ", ".join([f'{prof.get("professor_id", "N/A")}, {prof.get("name", "N/A")}' for prof in profs])
            print(f"{code} {name} - Year: {year}, Semester: {semester}")
            print(f"  Taught by: {professors_str}")
            print("-" * 60)
    else:
        print("Error retrieving module instances:", response.json())

def view_professor_ratings():
    response = session.get(BASE_URL + "professor-ratings/")
    if response.status_code == 200:
        ratings = response.json()
        for item in ratings:
            professor = item.get("professor", "Unknown")
            rating = item.get("rating", "Unrated")
            print(f"The rating of Professor {professor} is {rating}")
    else:
        print("Error retrieving professor ratings:", response.json())

def average_rating():
    professor_id = input("Enter professor id: ").strip()
    module_code = input("Enter module code: ").strip()
    url = f"{BASE_URL}average/{professor_id}/{module_code}/"
    token = session.headers.get("Authorization", "").split(" ")[1] if "Authorization" in session.headers else None
    headers = {"Authorization": f"Token {token}"} if token else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            avg_rating = data.get("average_rating", "Unrated")
            print(f"The average rating for Professor {data.get('professor', professor_id)} in module {data.get('module', module_code)} is {avg_rating}")
        except requests.exceptions.JSONDecodeError:
            print("Error: Response content is not valid JSON")
            print("Response content:", response.text)
    else:
        print("Error retrieving average rating:", response.text)

def rate_professor():
    token = session.headers.get("Authorization", "").split(" ")[1] if "Authorization" in session.headers else None
    if not token:
        print("You must be logged in to rate a professor.")
        return
    professor_id = input("Enter professor id: ").strip()
    module_code = input("Enter module code: ").strip()
    year = input("Enter teaching year: ").strip()
    semester = input("Enter semester (1 or 2): ").strip()
    rating_value = input("Enter rating (1-5): ").strip()
    data = {
        "professor_id": professor_id,
        "module_code": module_code,
        "year": year,
        "semester": semester,
        "rating": rating_value
    }
    headers = {"Authorization": f"Token {token}"}
    response = requests.post(BASE_URL + "rate/", json=data, headers=headers)
    if response.status_code == 201:
        print("Rating submitted successfully!")
    else:
        print("Error submitting rating:", response.text)

def main_menu():
    print("Available commands:")
    print(" register - Register a new user")
    print(" login    - Log in to your account")
    print(" logout   - Log out of your account")
    print(" list     - List all module instances")
    print(" view     - View overall professor ratings")
    print(" average  - View average rating for a professor in a module")
    print(" rate     - Rate a professor for a module instance")
    print(" exit     - Exit the client")

def main():
    print("Welcome to the Professor Rating Client")
    main_menu()
    while True:
        command = input(">> ").strip().lower()
        if command == "register":
            register()
        elif command == "login":
            login()
        elif command == "logout":
            logout()
        elif command == "list":
            list_module_instances()
        elif command == "view":
            view_professor_ratings()
        elif command == "average":
            average_rating()
        elif command == "rate":
            rate_professor()
        elif command in ("exit", "quit"):
            print("Exiting the client.")
            break
        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    main()
