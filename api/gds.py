import requests
from requests.utils import quote as encodeURL
import aiohttp
from http.cookies import SimpleCookie
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from api.constants import vals

# Headers to spoof looking like a genuine browser on the login website
global_headers = { 
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
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
    if(username == None or password == None):
        # If no password or username is provided, return a failure
        print('No username or password provided')
        return [0, 0]

    # Encode the username and password to be URL-safe
    username = encodeURL(username)
    password = encodeURL(password)

    # Get the URL to send the request to
    base = vals['domains']['MTSD']['base']
    login = vals['domains']['MTSD']['login']
    user_string = f"j_username={username}"
    pass_string = f"j_password={password}"
    url = base + login + "?" + user_string + "&" + pass_string

    # send a POST request with the username and password to the j_security Genesis verification page
    authenticated = False
    student_id = 0
    token = 0

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,ssl=False)) as session:
        verify_res = await genesis_request(session, method="POST", url=url, headers=global_headers, allow_redirects=False)
        authenticated = False
        if 'j_security_check' not in verify_res.headers['Location']:
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
        token = cookie_dict['JSESSIONID']
        
        try:
            log_res = requests.get(verify_res.headers['Location'], headers=global_headers, cookies=cookie_dict)
            split_url = urlparse(log_res.url)
            student_id = split_url.query.split('&')[2].split('=')[1]
        except Exception as e:
            print('Error occurred:', e)
            return
    

    # Return Success (only if still debugging/writing code)
    print("student_id: ", student_id, "token: ", token)
    return [student_id, token]

async def getGrades(username, password):
    login_result = await login(username, password)

    # Parse to see if there are any login errors; if not, return id and token
    if login_result == None:
        # If login fails (NoneType returned), return a 401 error
        return "401 Unauthorized"
    else:
        student_id = login_result[0]
        token = login_result[1]
    
    # Take the verification cookie and save it
    cookies = {'JSESSIONID': token}

    # Make a request to the gradebook
    url = vals['domains']['MTSD']['base'] + vals['domains']['MTSD']['gradebook'] + student_id + '&action=form'
    grade_page = requests.get(url, headers=global_headers, cookies=cookies)

    # Parse the HTML to get the grades
    soup = BeautifulSoup(grade_page.text, 'html.parser')
    table = soup.find('table', {'class': 'list'})
    rows = table.find_all('tr')

    # Remove the first row (headers) and every other row (separate grade table)
    rows.pop(0)
    rows = rows[::2]

    grades = []
    for row in rows:
        class_info = {}
        cells = row.find_all('td')
        cells = cells[0:3]

        cell_dev = []
        for i in range(len(cells)):
            cell_dev.append(cells[i].text.strip().split('\n')[0].split('\r')[0])
        print(cell_dev)


        for i in range(len(cells)):
            cells[i] = cells[i].text.strip()
            cell_info = cells[i].split('\n')[0].split('\r')[0]
            if i == 0:
                class_info['class'] = cell_info
            elif i == 1:
                class_info['teacher'] = cell_info
            elif i == 2:
                class_info['grade'] = cell_info
        grades.append(class_info)
    return grades