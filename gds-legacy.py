# def getGrades(user, password):
#     url = "https://parents.mtsd.k12.nj.us/genesis/sis/view?gohome=true"

#     user = user
#     password = password

#     driver = webdriver.Chrome()
#     driver.get(url)
#     driver.find_element(By.ID, "j_username").send_keys(user)
#     driver.find_element(By.ID, "j_password").send_keys(password)
#     driver.find_element(By.CLASS_NAME, "saveButton").click()

#     headerButtons = driver.find_elements(By.CLASS_NAME, "headerCategoryTab")
#     gradesButton = headerButtons[2]
#     gradesButton.click()

#     tables = driver.find_elements(By.TAG_NAME, 'table')
#     gradeTable = tables[2]
#     gradeRows = gradeTable.find_element(By.TAG_NAME, 'tbody').find_elements(By.XPATH, '*')
#     gradeRows.pop(0)

#     grades = []

#     for row in gradeRows:
#         grade = {}
#         grade['course'] = row.find_elements(By.TAG_NAME, 'td')[0].text
#         grade['teacher'] = row.find_elements(By.TAG_NAME, 'td')[1].text.split('\n')[0]
#         grade['grade'] = row.find_elements(By.TAG_NAME, 'td')[2].text
#         grades.append(grade)

#     return grades