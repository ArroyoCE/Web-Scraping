from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd


def is_element_in_viewport(driver, element):
    return driver.execute_script("""
        var elem = arguments[0];
        var rect = elem.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    """, element)

def is_at_bottom(driver):
    return driver.execute_script("""
        return (window.innerHeight + window.scrollY) >= document.body.offsetHeight;
    """)


def is_at_top(driver):
    return driver.execute_script("""
        // Check if we can scroll up
        var prevScrollY = window.scrollY;
        window.scrollBy(0, -10);
        var currentScrollY = window.scrollY;

        // Restore the previous scroll position
        window.scrollTo(0, prevScrollY);

        // If we couldn't scroll up, we're at the top
        return prevScrollY === currentScrollY;
    """)

def scroll_until_button_visible(driver, button_xpath, max_duration=150):
    start_time = time.time()
    scroll_step = 500
    controle = 1
    contador = 0

    while time.time() - start_time < max_duration:
        for _ in range(70):  # Scroll down in steps
            if controle == 1:
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                contador = contador + 1
            else:
                driver.execute_script(f"window.scrollBy(0, {-scroll_step});")
            time.sleep(2)  # Wait for content to load

            try:
                button = driver.find_element(By.XPATH, button_xpath)
                if button.is_displayed() and is_element_in_viewport(driver, button):
                    print("'Mostrar mais' button is now visible and in viewport.")
                    return True
            except NoSuchElementException:
                pass  # Button not found, continue scrolling

            # Check if we've reached the bottom of the page
            if is_at_bottom(driver):
                controle = -1
            elif is_at_top(driver) or contador == 5:
                controle = 1

        # Update scroll step in case page height has changed
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_step = max(400, page_height // 10)  # Ensure minimum scroll step of 30 pixels

    print(f"Reached maximum scrolling duration of {max_duration} seconds.")
    return False


def extract_product_info(element):
    try:
        discount_flag = element.find_element(By.CLASS_NAME,
                                             "rihappyio-rihappy-store-components-0-x-discountFlagPercentage")

        product_name = element.find_element(By.CLASS_NAME, "vtex-product-summary-2-x-productBrand").text

        original_price_elements = element.find_elements(By.CSS_SELECTOR,
                                                        ".vtex-product-price-1-x-currencyInteger--list-price-product-summary, .vtex-product-price-1-x-currencyDecimal--list-price-product-summary, .vtex-product-price-1-x-currencyFraction--list-price-product-summary")
        original_price = ''.join([e.text for e in original_price_elements]).replace(',', '.')

        new_price_elements = element.find_elements(By.CSS_SELECTOR,
                                                   ".vtex-product-price-1-x-currencyInteger--shelf-price-discount, .vtex-product-price-1-x-currencyDecimal--shelf-price-discount, .vtex-product-price-1-x-currencyFraction--shelf-price-discount")
        new_price = ''.join([e.text for e in new_price_elements]).replace(',', '.')

        discount_rate = discount_flag.text

        return {
            'product_name': product_name,
            'original_price': float(original_price),
            'new_price': float(new_price),
            'discount_rate': discount_rate
        }
    except NoSuchElementException:
        return None


def save_elements(driver, name):
    products = driver.find_elements(By.CLASS_NAME, "vtex-product-summary-2-x-element")
    product_data = []

    for product in products:
        info = extract_product_info(product)
        if info:
            product_data.append(info)

    df = pd.DataFrame(product_data)
    df.to_excel(f'product_discounts{name}.xlsx', index=False)
    print(f"Saved {len(product_data)} products to product_discounts.xlsx")


def load_all_products(url, name):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        print("Waiting 5 seconds for the page to load completely...")
        time.sleep(5)

        # Handle the CEP input
        try:
            cep_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Digite o seu CEP...']"))
            )
            cep_input.click()
            cep_input.send_keys(14021578)

            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'vtex-button__label') and contains(text(), 'quero ofertas')]"))
            )
            button.click()
            print("Clicked 'quero ofertas' button. Waiting for page to update...")
        except TimeoutException:
            print("CEP input not found or already handled. Proceeding with next steps.")

        # Wait and check for the "Dispensar" button with a longer timeout
        print("Waiting up to 30 seconds for the 'Dispensar' button to appear...")
        time.sleep(10)
        try:
            dispensar_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@class='cc-btn cc-dismiss cc-btn-format' and contains(text(), 'Dispensar')]"))
            )
            dispensar_button.click()
            print("Clicked 'Dispensar' button.")
            time.sleep(2)  # Wait for any animations or page updates after clicking
        except TimeoutException:
            print("'Dispensar' button not found or not clickable after 30 seconds. Proceeding with product loading.")

        mostrar_mais_xpath = "//a[contains(@class, 'vtex-button') and .//div[contains(text(), 'Mostrar mais')]]"
        product_count_xpath = "//span[contains(@class, 'vtex-search-result-3-x-showingProductsCount')]"

        while True:
            print("Scrolling until 'Mostrar mais' button is visible...")
            button_visible = scroll_until_button_visible(driver, mostrar_mais_xpath)
            time.sleep(5)

            try:
                product_count_element = driver.find_element(By.XPATH, product_count_xpath)
                product_count_text = product_count_element.text
                current, total = map(int, product_count_text.split()[::2])
                print(f"Currently showing {current} out of {total} products")

                if current >= total/2:
                    print("All products loaded successfully!")
                    save_elements(driver, name)
                    break
            except NoSuchElementException:
                print("Couldn't find product count element. Continuing to load more.")

            if not button_visible:
                print("'Mostrar mais' button not found after scrolling. Checking if all products are loaded.")
                continue

            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, mostrar_mais_xpath))
                )
                button.click()
                print("Clicked 'Mostrar mais' button. Waiting for new products to load...")
                time.sleep(8)  # Wait for new products to start loading
            except TimeoutException:
                print("Failed to click 'Mostrar mais' button. Checking if all products are loaded.")

    finally:
        driver.quit()
