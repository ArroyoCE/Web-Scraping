from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException
import time
import re


def setup_driver(visible=False, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            chrome_options = webdriver.ChromeOptions()
            if not visible:
                chrome_options.add_argument('--headless')

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except WebDriverException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise
            time.sleep(2)


def wait_for_login(driver, timeout=600):  # 10 minutes timeout
    landing_page = "https://eproc.trf4.jus.br/eproc2trf4"
    post_login_url = "https://eproc.trf4.jus.br/eproc2trf4/controlador.php?acao=painel_adv_listar&acao_origem=principal"

    driver.get(landing_page)
    print("Waiting for user to log in...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        if post_login_url in driver.current_url:
            print("Login successful!")
            return True
        time.sleep(1)  # Check every second

    print("Login timeout reached.")
    return False


def navigate_to_processo_consultar(driver):
    try:
        # Wait for and click "Consulta Processual" dropdown
        consulta_processual = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Consulta Processual']"))
        )
        consulta_processual.click()

        # Wait for and click "Consultar Processos"
        consultar_processos = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Consultar Processos']"))
        )
        consultar_processos.click()

        # Wait for the new page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("https://eproc.trf4.jus.br/eproc2trf4/controlador.php?acao=processo_consultar")
        )

        print("Successfully navigated to Consultar Processos page.")
    except WebDriverException as e:
        print(f"Error during navigation: {e}")
        raise


def get_valid_suit_number():
    pattern = re.compile(r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$')
    while True:
        suit_number = input("Please enter the Suit Number (format: 0000000-00.0000.0.00.0000): ")
        if pattern.match(suit_number):
            return suit_number
        else:
            print("Invalid format. Please try again.")


def consult_process(driver):
    try:
        # Get valid suit number from user
        suit_number = get_valid_suit_number()

        # Find and fill the input field
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "numNrProcesso"))
        )
        input_field.clear()
        input_field.send_keys(suit_number)

        # Find and click the submit button
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "sbmConsultar"))
        )
        submit_button.click()

        print(f"Consulted process number: {suit_number}")
    except WebDriverException as e:
        print(f"Error during process consultation: {e}")
        raise


def access_process_integrity(driver):
    try:
        # Wait for and click "Acesso íntegra do processo" link
        access_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Acesso íntegra do processo')]"))
        )
        access_link.click()

        print("Clicked on 'Acesso íntegra do processo' link.")

        # Switch to the new window
        driver.switch_to.window(driver.window_handles[-1])

        # Wait for CAPTCHA to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'captcha')]"))
            )
            print("CAPTCHA detected. Please solve the CAPTCHA manually.")
            input("Press Enter after solving the CAPTCHA...")
        except TimeoutException:
            print("CAPTCHA not detected or page loaded without CAPTCHA.")

    except WebDriverException as e:
        print(f"Error while accessing process integrity: {e}")
        raise


def main():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            driver = setup_driver(visible=False)

            if wait_for_login(driver):
                print("Window is hidden. Site is active with generated cookies.")

                navigate_to_processo_consultar(driver)
                consult_process(driver)
                access_process_integrity(driver)

                print("Process completed. You may now interact with the page.")
                input("Press Enter to exit and close the browser...")
                break
            else:
                print("Login was not successful within the timeout period.")
                break
        except WebDriverException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                print("Max attempts reached. Please try running the script again.")
            else:
                print("Retrying...")
                time.sleep(2)
        finally:
            if 'driver' in locals():
                driver.quit()


if __name__ == "__main__":
    main()