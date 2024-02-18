import requests
from requests.utils import quote as encodeURL
import aiohttp
from http.cookies import SimpleCookie
from urllib.parse import urlparse
from bs4 import BeautifulSoup, NavigableString
from api.constants import vals

# Headers to spoof looking like a genuine browser on the login website
global_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) "
    "Gecko/20100101 Firefox/113.0",
}


async def genesis_request(session, method, *args, **kwargs):
    if method == "GET":
        async with session.get(*args, **kwargs) as response:
            return response
    elif method == "POST":
        async with session.post(*args, **kwargs) as response:
            return response


async def login(username, password):
    # Format username and password into URL-encoded strings
    if username is None or password is None:
        # If no password or username is provided, return a failure
        print("No username or password provided")
        return [0, 0]

    # Encode the username and password to be URL-safe
    username = encodeURL(username)
    password = encodeURL(password)

    # Get the URL to send the request to
    base = vals["domains"]["MTSD"]["base"]
    login = vals["domains"]["MTSD"]["login"]
    user_string = f"j_username={username}"
    pass_string = f"j_password={password}"
    url = base + login + "?" + user_string + "&" + pass_string

    # send a POST request to Genesis verification page
    authenticated = False
    student_id = 0
    token = 0

    proxy_req = requests.get("http://localhost:3000/get-proxies").text

    proxies = {"http": proxy_req}
    print(proxy_req)
    print("Routing through: " + proxy_req)

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=64, ssl=False)
    ) as session:
        verify_res = await genesis_request(
            session,
            method="POST",
            url=url,
            headers=global_headers,
            allow_redirects=False,
        )
        authenticated = False
        if "j_security_check" not in verify_res.headers["Location"]:
            authenticated = True

        # If not authenticated, exit and return failure
        if not authenticated:
            return

        # Get cookies from the response to login to main page
        cookies = SimpleCookie()
        cookies.load(verify_res.cookies)

        cookie_dict = {}
        for key, morsel in cookies.items():
            cookie_dict[key] = morsel.value

        # Get the student ID from the response
        token = cookie_dict["JSESSIONID"]

        try:
            log_res = requests.get(
                verify_res.headers["Location"],
                headers=global_headers,
                cookies=cookie_dict,
                proxies=proxies,
            )
            split_url = urlparse(log_res.url)
            student_id = split_url.query.split("&")[2].split("=")[1]
        except Exception as e:
            print("Error occurred:", e)
            return

    # Return Success (only if still debugging/writing code)
    print("student_id: ", student_id, "token: ", token)
    return [student_id, token]


async def getGrades(username, password):
    login_result = await login(username, password)

    # Parse to see if there are any login errors; if not, return id and token
    if login_result is None:
        # If login fails (NoneType returned), return a 401 error
        return "401 Unauthorized"
    else:
        student_id = login_result[0]
        token = login_result[1]

    # Take the verification cookie and save it
    cookies = {"JSESSIONID": token}

    # Make a request to the gradebook
    url = (
        vals["domains"]["MTSD"]["base"]
        + vals["domains"]["MTSD"]["gradebook"]
        + student_id
        + "&action=form"
    )
    grade_page = requests.get(url, headers=global_headers, cookies=cookies)

    # Parse the HTML to get the grades
    soup = BeautifulSoup(grade_page.text, "html.parser")
    class_grades_container = soup.find("div", {"class": "itemContainer"})

    grades = []
    for element in class_grades_container:
        class_info = {}
        if not isinstance(element, NavigableString):
            span_list = element.find_all("span")
            if len(span_list) == 1:
                class_info["course_name"] = span_list[0].text.strip()
                class_info["grade"] = "No grade yet"
            else:
                class_info["course_name"] = span_list[1].text.strip()
                class_info["grade"] = span_list[0].text.strip()
            grades.append(class_info)

    return grades
