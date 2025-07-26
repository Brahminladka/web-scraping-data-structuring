from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import pandas as pd
import time

class BestBuyStoreScraper:
    def __init__(self):
        self.base_url = "https://www.bestbuy.com"
        self.locator_url = f"{self.base_url}/site/store-locator"
        self.driver = None

    def init_browser(self):
        """Initialize browser with optimal settings"""
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        
        service = Service('msedgedriver.exe')
        service.creationflags = 0x08000000
        
        try:
            self.driver = webdriver.Edge(service=service, options=options)
            self.driver.set_page_load_timeout(45)
            return True
        except Exception as e:
            print(f"Browser initialization failed: {e}")
            return False

    def scrape_stores(self, zip_code='10001'):
        """Main scraping function with proper time delays"""
        if not self.init_browser():
            return pd.DataFrame()
            
        try:
            print("\nStarting Best Buy store search...")
            
            # Load the page with initial delay
            print("Opening website...")
            self.driver.get(self.locator_url)
            time.sleep(8)
            
            # Wait for zip code input to be present and interactive
            print("Waiting for page elements to load...")
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.zip-code-input")))
            time.sleep(3)
            
            # Enter zip code with proper pacing
            print(f"Entering zip code: {zip_code}")
            zip_input = self.driver.find_element(By.CSS_SELECTOR, "input.zip-code-input")
            zip_input.clear()
            time.sleep(2)
            zip_input.send_keys(zip_code)
            time.sleep(3)
            
            # Click search button with verification
            search_btn = self.driver.find_element(By.CSS_SELECTOR, "button.location-zip-code-form-update-btn")
            print("Clicking search button...")
            search_btn.click()
            time.sleep(10)
            
            # Wait for results with proper timeout
            print("Waiting for store results...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.store")))
            time.sleep(5)
            
            return self.extract_store_data()
            
        except Exception as e:
            print(f"Scraping failed: {e}")
            return pd.DataFrame()
        finally:
            if self.driver:
                self.driver.quit()

    def get_store_details(self, details_url):
        """Extract phone and services from store details page"""
        try:
            # Open details page in new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(details_url)
            time.sleep(8)
            
            # Extract phone number with multiple fallback methods
            phone = self.extract_phone_number()
            
            # Extract services
            services = self.extract_services()
            
            # Close details tab and return to main window
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(3)
            
            return phone, services
            
        except Exception as e:
            print(f"Error processing details page: {e}")
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            return "N/A", []

    def extract_phone_number(self):
        """Robust phone number extraction with multiple fallbacks"""
        try:
            # Method 1: Try getting from visible phone link text
            phone_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='tel:'] span")))
            phone = phone_element.text.strip()
            if phone:
                return phone
        except:
            pass
            
        try:
            # Method 2: Try getting from hidden phone span
            phone_element = self.driver.find_element(By.CSS_SELECTOR, "span.hidden.sm\\:inline")
            phone = phone_element.text.strip()
            if phone:
                return phone
        except:
            pass
            
        try:
            # Method 3: Extract from href attribute
            phone_element = self.driver.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
            phone = phone_element.get_attribute("href").replace("tel:", "").strip()
            if phone:
                return phone
        except:
            pass
            
        try:
            # Method 4: Look for phone number in flex container
            phone_container = self.driver.find_element(By.CSS_SELECTOR, "div.flex.items-center")
            phone_elements = phone_container.find_elements(By.TAG_NAME, "span")
            for element in phone_elements:
                text = element.text.strip()
                if "(" in text and ")" in text:  # Basic phone number format check
                    return text
        except:
            pass
            
        return "N/A"

    def extract_services(self):
        """Extract services from current page"""
        services = []
        try:
            service_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.grid.md\\:grid-cols-2.lg\\:grid-cols-3")))
            service_items = service_container.find_elements(By.CSS_SELECTOR, "li.flex.py-2")
            services = [item.find_element(By.CSS_SELECTOR, "div:last-child").text.strip() 
                      for item in service_items if item.text.strip()]
        except:
            pass
        return services

    def extract_store_data(self):
        """Extract store data with proper loading waits"""
        stores = []
        store_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.store")
        
        print(f"Found {len(store_elements)} stores - extracting details...")
        
        for store in store_elements:
            try:
                # Scroll to element with pause
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", store)
                time.sleep(5)
                
                # Extract basic info
                name = store.find_element(By.CSS_SELECTOR, "[data-cy='store-heading']").text
                address = store.find_element(By.CSS_SELECTOR, "[data-cy='AddressComponent']").text
                hours = store.find_element(By.CSS_SELECTOR, "[data-cy='BusinessHoursComponent']").text
                distance = store.find_element(By.CSS_SELECTOR, "[data-cy='LocationDistance']").text
                store_id = store.get_attribute("data-store-id")
                
                # Get details link
                details_link = store.find_element(By.CSS_SELECTOR, "a.details[data-cy='DetailsComponent']")
                details_url = details_link.get_attribute("href")
                
                # Get phone and services from details page
                phone, services = self.get_store_details(details_url)
                
                stores.append({
                    'Store Name': name,
                    'Address': address.replace('\n', ', '),
                    'Phone': phone,
                    'Hours': hours.replace('\n', '; '),
                    'Distance': distance,
                    'Store ID': store_id,
                    'Services': ', '.join(services) if services else 'N/A',
                    'Details URL': details_url
                })
                
            except Exception as e:
                print(f"Error processing store: {e}")
                continue
                
        return pd.DataFrame(stores)

def main():
    print("=== Best Buy Store Locator ===")
    
    scraper = BestBuyStoreScraper()
    results = scraper.scrape_stores('10001')
    
    if not results.empty:
        output_file = "bestbuy_stores_with_details.csv"
        results.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        print("\nSample data:")
        print(results[['Store Name', 'Phone', 'Services']].head())
    else:
        print("\nNo stores found or scraping failed")

if __name__ == "__main__":
    main()