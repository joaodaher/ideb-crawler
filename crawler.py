import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _wait_for(driver, value, by=By.ID, timeout=20):
    element_present = EC.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(element_present)


def _select(driver, element_id, value):
    e = driver.find_element_by_id(element_id)
    select = Select(e)

    options = e.text.strip().split('\n')
    select.select_by_index(options.index(value))


def extract_school_paths(driver):
    target = 'coluna'

    _wait_for(driver=driver, by=By.CLASS_NAME, value=target)

    paths = []
    for row in driver.find_elements_by_class_name(target):
        path = row.get_attribute("onclick").replace('location.href = ', '').replace('"', '')
        paths.append(path)
    return paths


def run(uf, city):
    import os
    driver_path = os.path.join(os.path.dirname(__file__), 'geckodriver')


    driver = webdriver.Firefox(executable_path=driver_path)
    driver.get("http://idebescola.inep.gov.br/ideb/consulta-publica")

    _select(driver=driver, element_id='pkCodEstado', value=uf.upper())
    _select(driver=driver, element_id='pkCodMunicipio', value=city.upper())

    driver.find_element_by_id('frm').submit()

    for path in extract_school_paths(driver=driver):
        source = _handle_school(driver=driver, path=path)
        write(name=path.split('/')[-1], source=source)

    driver.close()


def write(name, source):
    path = os.path.join('.', 'sources', f'{name}.html')
    with open(path, 'w') as f:
        f.write(source)


def _open_accordion(driver, element_id):
    _wait_for(driver=driver, by=By.ID, value=element_id, timeout=10)
    e = driver.find_element_by_id(element_id)
    e.click()
    time.sleep(2)
    e.click()
    time.sleep(2)


def _handle_school(driver, path):
    url = f'http://idebescola.inep.gov.br/ideb/{path}'
    driver.get(url)

    suffixes = ['One', 'Two', 'Tree', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']

    for suffix in suffixes:
        element_id = f'target-collapse{suffix}'
        _open_accordion(driver=driver, element_id=element_id)

    return driver.page_source


if __name__ == '__main__':
    run(uf="Minas Gerais", city="Passos")
