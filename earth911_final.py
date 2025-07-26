"""
Earth911 Recycling Locator Scraper
A robust script to collect recycling center information from Earth911.com
"""

import time
from datetime import datetime
from urllib.parse import urljoin
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup

class Earth911Scraper:
    def __init__(self):
        self.driver = None
        self.base_url = "https://search.earth911.com/"
        
    def clean_text(self, text):
        """Clean and normalize text by removing special characters"""
        if not text:
            return ""
        text = re.sub(r'[\uFEFF\u00A0\u200B]+', '', text)
        return ' '.join(text.split()).strip()
    
    def parse_date(self, date_str):
        """Convert date string to YYYY-MM-DD format"""
        try:
            date_obj = datetime.strptime(date_str.strip(), '%b %d, %Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return datetime.now().strftime('%Y-%m-%d')
    
    def setup_driver(self):
        """Initialize the Edge WebDriver with proper configuration"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        try:
            service = Service('msedgedriver.exe')
            self.driver = webdriver.Edge(service=service, options=options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Failed to initialize WebDriver: {e}")
            return False
    
    def get_last_updated_date(self, detail_url):
        """Get the last updated date from a location's detail page"""
        self.driver.get(detail_url)
        time.sleep(2)
        
        try:
            date_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.last-verified")))
            date_text = date_element.text.replace('Updated', '').strip()
            return self.parse_date(date_text)
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def process_location(self, location, materials_category):
        """Process a single location listing"""
        try:
            # Extract basic information
            name_element = location.find('h2', class_='title')
            name = self.clean_text(name_element.get_text()) if name_element else "Unknown"
            
            # Build address
            addr1 = self.clean_text(location.find('p', class_='address1').get_text()) if location.find('p', class_='address1') else ''
            addr3 = self.clean_text(location.find('p', class_='address3').get_text()) if location.find('p', class_='address3') else ''
            full_address = f"{addr1}, {addr3}".strip(', ')
            
            # Get accepted materials
            materials_div = location.find('p', class_='result-materials')
            materials = []
            if materials_div:
                materials = [self.clean_text(m.get_text()) for m in materials_div.find_all('span', class_='matched')]
            
            # Get detail page URL
            detail_link = name_element.find('a')['href'] if name_element and name_element.find('a') else None
            if not detail_link:
                return None
                
            detail_url = urljoin(self.base_url, detail_link)
            last_updated = self.get_last_updated_date(detail_url)
            
            # Return to search results
            self.driver.back()
            time.sleep(1)
            
            return {
                'Business Name': name,
                'Last Updated': last_updated,
                'Address': full_address,
                'Materials Category': materials_category,
                'Accepted Materials': ', '.join(materials)
            }
            
        except Exception as e:
            print(f"Error processing location: {e}")
            return None
    
    def scrape_page(self, url, materials_category):
        """Scrape all locations from a single page"""
        self.driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        locations = soup.find_all('li', class_='result-item')
        page_data = []
        
        for location in locations:
            location_data = self.process_location(location, materials_category)
            if location_data:
                page_data.append(location_data)
        
        return page_data
    
    def has_next_page(self):
        """Check if there's a next page available"""
        try:
            next_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.next")))
            return next_button.get_attribute('href')
        except Exception:
            return None
    
    def scrape(self, material_type='Electronics', location='10001', max_distance=25, max_pages=3):
        """Main scraping function with pagination support"""
        if not self.setup_driver():
            return pd.DataFrame()
        
        try:
            # Build initial search URL
            params = {
                'what': material_type,
                'where': location,
                'max_distance': max_distance,
                'list_filter': 'all',
                'country': 'US'
            }
            current_url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
            
            all_data = []
            pages_scraped = 0
            
            while current_url and pages_scraped < max_pages:
                pages_scraped += 1
                print(f"Scraping page {pages_scraped}...")
                
                page_data = self.scrape_page(current_url, material_type)
                all_data.extend(page_data)
                print(f"Found {len(page_data)} locations")
                
                current_url = self.has_next_page()
            
            return pd.DataFrame(all_data)
        
        except Exception as e:
            print(f"Scraping error: {e}")
            return pd.DataFrame()
        finally:
            if self.driver:
                self.driver.quit()
                print("WebDriver closed.")

def main():
    """Run the scraper and save results"""
    print("=== Earth911 Recycling Locator ===")
    print("Starting scraping process...\n")
    
    scraper = Earth911Scraper()
    results = scraper.scrape(
        material_type='Electronics',
        location='10001',
        max_distance=100,
        max_pages=-1  # Set to -1 for unlimited pages
    )
    
    if not results.empty:
        output_file = 'recycling_locations.csv'
        results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nSuccess! Saved {len(results)} locations to {output_file}")
        print("\nSample results:")
        print(results.head())
    else:
        print("\nNo data was collected. Please check:")
        print("- Is msedgedriver.exe in the same folder?")
        print("- Is your internet connection working?")
        print("- Try reducing the max_pages parameter")

if __name__ == "__main__":
    main()