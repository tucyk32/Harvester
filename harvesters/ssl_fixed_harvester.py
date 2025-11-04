#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ssl_fixed_harvester.py
-----------------------
Simplified harvester with SSL issues fixed for real-world data collection.
"""

import asyncio
import aiohttp
import pandas as pd
import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import hashlib
import time
import logging
import ssl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSLFixedHarvester:
    def __init__(self):
        self.session = None
        
    async def get_session(self):
        """Create session with SSL issues fixed"""
        if not self.session:
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(
                limit=50,
                ssl=ssl_context
            )
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'DataHarvester/1.0 (Educational)'}
            )
        return self.session
    
    async def test_arxiv_harvest(self, keyword: str = "history", max_results: int = 10):
        """Test arXiv harvesting with SSL fix"""
        logger.info(f"🔬 Testing arXiv harvest for '{keyword}'")
        
        try:
            query = f'all:"{keyword}"'
            url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_results}"
            
            session = await self.get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    papers = self.parse_arxiv_xml(xml_content)
                    logger.info(f"✅ Successfully harvested {len(papers)} papers from arXiv")
                    return papers
                else:
                    logger.error(f"❌ arXiv returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ arXiv harvest failed: {e}")
            return []
    
    def parse_arxiv_xml(self, xml_content: str):
        """Parse arXiv XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                
                if title_elem is not None and published_elem is not None:
                    # Parse date
                    pub_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                    
                    # Calculate Julian Day
                    jd = self._date_to_jd(pub_date.year, pub_date.month, pub_date.day)
                    am_day = jd - 1738164.0
                    
                    paper = {
                        'title': title_elem.text.strip() if title_elem.text else '',
                        'abstract': summary_elem.text.strip() if summary_elem is not None and summary_elem.text else '',
                        'publication_date': pub_date.strftime('%Y-%m-%d'),
                        'source_database': 'arxiv',
                        'url': id_elem.text if id_elem is not None and id_elem.text else '',
                        'year_abs': pub_date.year,
                        'jd': jd,
                        'am_day': am_day
                    }
                    
                    papers.append(paper)
                    
        except Exception as e:
            logger.error(f"Error parsing arXiv XML: {e}")
        
        return papers
    
    async def test_wikipedia_harvest(self, language: str = "en", year: int = 2023):
        """Test Wikipedia harvesting"""
        logger.info(f"📚 Testing Wikipedia harvest for {language}.wikipedia.org year {year}")
        
        try:
            url = f"https://{language}.wikipedia.org/wiki/{year}"
            
            session = await self.get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Simple extraction - count mentions of months
                    months = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
                    
                    events = []
                    for month in months:
                        if month in content:
                            jd = self._date_to_jd(year, months.index(month) + 1, 15)
                            am_day = jd - 1738164.0
                            
                            event = {
                                'title': f'Events in {month} {year}',
                                'content': f'Wikipedia page for {year} mentions events in {month}',
                                'date_str': f'{year}-{months.index(month) + 1:02d}-15',
                                'year_abs': year,
                                'source': f'wikipedia_{language}',
                                'url': url,
                                'jd': jd,
                                'am_day': am_day
                            }
                            events.append(event)
                    
                    logger.info(f"✅ Extracted {len(events)} events from Wikipedia")
                    return events
                else:
                    logger.error(f"❌ Wikipedia returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Wikipedia harvest failed: {e}")
            return []
    
    async def test_pubmed_harvest(self, keyword: str = "history", max_results: int = 5):
        """Test PubMed harvesting using E-utilities"""
        logger.info(f"🧬 Testing PubMed harvest for '{keyword}'")
        
        try:
            # PubMed E-utilities search
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': keyword,
                'retmax': max_results,
                'retmode': 'json'
            }
            
            session = await self.get_session()
            async with session.get(search_url, params=search_params) as response:
                if response.status == 200:
                    search_data = await response.json()
                    
                    if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                        pmids = search_data['esearchresult']['idlist']
                        
                        if pmids:
                            # Fetch details
                            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                            fetch_params = {
                                'db': 'pubmed',
                                'id': ','.join(pmids[:5]),  # Limit to 5
                                'retmode': 'xml'
                            }
                            
                            # Add small delay for rate limiting
                            await asyncio.sleep(1)
                            
                            async with session.get(fetch_url, params=fetch_params) as fetch_response:
                                if fetch_response.status == 200:
                                    xml_content = await fetch_response.text()
                                    papers = self.parse_pubmed_xml(xml_content)
                                    logger.info(f"✅ Successfully harvested {len(papers)} papers from PubMed")
                                    return papers
                                    
        except Exception as e:
            logger.error(f"❌ PubMed harvest failed: {e}")
            return []
        
        return []
    
    def parse_pubmed_xml(self, xml_content: str):
        """Parse PubMed XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                # Extract title
                title_elem = article.find('.//ArticleTitle')
                title = title_elem.text if title_elem is not None and title_elem.text else 'Unknown title'
                
                # Extract abstract
                abstract_elem = article.find('.//Abstract/AbstractText')
                abstract = abstract_elem.text if abstract_elem is not None and abstract_elem.text else ''
                
                # Extract publication date
                pub_date_elem = article.find('.//PubDate')
                year = 2000  # Default
                
                if pub_date_elem is not None:
                    year_elem = pub_date_elem.find('Year')
                    if year_elem is not None and year_elem.text:
                        try:
                            year = int(year_elem.text)
                        except ValueError:
                            year = 2000
                
                # Calculate Julian Day
                jd = self._date_to_jd(year, 6, 15)  # Mid-year estimate
                am_day = jd - 1738164.0
                
                paper = {
                    'title': title,
                    'abstract': abstract[:500],  # Truncate abstract
                    'publication_date': f"{year}-06-15",
                    'source_database': 'pubmed',
                    'year_abs': year,
                    'jd': jd,
                    'am_day': am_day
                }
                
                papers.append(paper)
                
        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {e}")
        
        return papers
    
    def _date_to_jd(self, year: int, month: int, day: int) -> float:
        """Convert date to Julian Day"""
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        if year >= 1583 or (year == 1582 and month >= 10 and day >= 15):
            b = 2 - a + a // 4
        else:
            b = 0
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        return jd
    
    def save_to_csv(self, data: list, filename: str):
        """Save harvested data to CSV"""
        if data:
            df = pd.DataFrame(data)
            output_path = Path(filename)
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"💾 Saved {len(data)} records to {output_path}")
            return output_path
        else:
            logger.warning("No data to save")
            return None
    
    async def run_comprehensive_test(self):
        """Run comprehensive harvesting test"""
        logger.info("🚀 Starting comprehensive harvesting test")
        
        all_data = []
        
        # Test arXiv
        arxiv_papers = await self.test_arxiv_harvest("medieval", 15)
        all_data.extend(arxiv_papers)
        
        # Test Wikipedia  
        wiki_events = await self.test_wikipedia_harvest("en", 2023)
        all_data.extend(wiki_events)
        
        # Test PubMed
        pubmed_papers = await self.test_pubmed_harvest("archaeological", 10)
        all_data.extend(pubmed_papers)
        
        # Save results
        if all_data:
            csv_path = self.save_to_csv(all_data, "real_harvested_data.csv")
            
            logger.info(f"✅ Comprehensive test completed!")
            logger.info(f"📊 Total records harvested: {len(all_data)}")
            logger.info(f"💾 Data saved to: {csv_path}")
            
            # Show breakdown
            sources = {}
            for record in all_data:
                source = record.get('source_database', record.get('source', 'unknown'))
                sources[source] = sources.get(source, 0) + 1
            
            logger.info("📈 Sources breakdown:")
            for source, count in sources.items():
                logger.info(f"  {source}: {count} records")
        
        return all_data
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main test function"""
    harvester = SSLFixedHarvester()
    
    try:
        # Run comprehensive test
        data = await harvester.run_comprehensive_test()
        
        print(f"\n🎉 SSL-Fixed Harvesting Test Completed!")
        print(f"📊 Successfully harvested {len(data)} records from multiple sources")
        
        if data:
            print(f"\n📋 Sample records:")
            for i, record in enumerate(data[:3]):
                print(f"  {i+1}. {record.get('title', 'No title')[:60]}...")
        
    finally:
        await harvester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())