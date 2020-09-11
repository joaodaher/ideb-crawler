import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _wait_for(driver, value, by=By.ID, timeout=20):
    '''
    Sometimes the page loads but not all desired elements are available.
    This method waits for an element to be selectable in the page.
    :param driver: Selenium webdriver
    :param value: Element value
    :param by: Selenium's By (eg. ID, class, name)
    :param timeout: Maximum time to wait for the element before failing
    :return: None
    '''
    element_present = EC.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(element_present)


def _select(driver, element_id, value):
    '''
    The IDEP's dropdowns are not properly configured with options,
    so the strategy is to find the item and select by its position.
    :param driver: Selenium webdriver
    :param element_id: Dropdown element ID
    :param value: Option to be selected
    :return: None
    '''
    e = driver.find_element_by_id(element_id)
    select = Select(e)

    options = e.text.strip().split('\n')
    select.select_by_index(options.index(value))


def _extract_school_paths(driver):
    '''
    When the browser is in the city's schools page list,
    this method extracts every school ID
    :param driver: Selenium webdriver
    :return: List of school paths
    '''
    target = 'coluna'

    _wait_for(driver=driver, by=By.CLASS_NAME, value=target)

    paths = []
    for row in driver.find_elements_by_class_name(target):
        path = row.get_attribute("onclick").replace('location.href = ', '').replace('"', '')
        paths.append(path)
    return paths


def _write(name, source):
    '''
    Write a HTML source to a file
    :param name: File name
    :param source: HTML data
    :return: None
    '''
    path = os.path.join('.', 'sources', f'{name}.html')
    with open(path, 'w') as f:
        f.write(source)


def _open_accordion(driver, element_id, wait=2):
    '''
    Gently open and close an accordion.
    :param driver: Selenium web driver
    :param element_id: Accordion element ID
    :return: None
    '''
    _wait_for(driver=driver, by=By.ID, value=element_id)
    e = driver.find_element_by_id(element_id)
    e.click()
    time.sleep(wait)
    e.click()
    time.sleep(wait)


def _handle_school(driver, path):
    '''
    The school page has dynamic content, triggered by ajax calls in multiple accordions.
    These accordions must be opened and closed, in order to the buttons do not change their initial positions.
    :param driver: Selenium web driver
    :param path: school path
    :return: HTML page source
    '''
    url = f'http://idebescola.inep.gov.br/ideb/{path}'
    driver.get(url)

    suffixes = ['One', 'Two', 'Tree', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']

    for suffix in suffixes:
        element_id = f'target-collapse{suffix}'
        _open_accordion(driver=driver, element_id=element_id)

    return driver.page_source


def _search(driver, uf, city):
    '''
    Given an UF and city, fill out and submit the search form
    :param driver: Selenium webdriver
    :param uf: UF name
    :param city: City name
    :return: None
    '''
    driver.get("http://idebescola.inep.gov.br/ideb/consulta-publica")

    _select(driver=driver, element_id='pkCodEstado', value=uf.upper())
    _select(driver=driver, element_id='pkCodMunicipio', value=city.upper())

    driver.find_element_by_id('frm').submit()


def run(uf, city):
    '''
    Stores the school page HTML into a file inside ./sources folder
    :param uf: UF name, as shown in dropbox
    :param city: City name, as shown in dropbox
    :return: None
    '''
    driver_path = os.path.join(os.path.dirname(__file__), 'geckodriver')
    driver = webdriver.Firefox(executable_path=driver_path)

    _search(driver=driver, uf=uf, city=city)

    for path in _extract_school_paths(driver=driver):
        source = _handle_school(driver=driver, path=path)
        _write(name=path.split('/')[-1], source=source)

    driver.close()


if __name__ == '__main__':
    run(uf="Minas Gerais", city="Passos")
