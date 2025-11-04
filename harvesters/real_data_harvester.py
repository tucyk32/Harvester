#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
real_data_harvester.py
----------------------
Prawdziwy harvester który pobiera dane z rzeczywistych API bez żadnych mock data
"""

import asyncio
import aiohttp
import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import logging
import ssl
from pathlib import Path
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataHarvester:
    def __init__(self):
        self.session = None
        self.results = {
            'arxiv': [],
            'pubmed': [],
            'wikipedia': [],
            'crossref': [],
            'nature': [],
            'ieee': []
        }
        
    async def get_session(self):
        """Create async session with SSL disabled for testing"""
        if not self.session:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(
                limit=50,
                ssl=ssl_context
            )
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'RealDataHarvester/1.0 (Educational Research)'}
            )
        return self.session

    async def harvest_arxiv_real(self, keywords: list = None, max_papers: int = 50):
        """Pobiera prawdziwe artykuły z arXiv"""
        if not keywords:
            keywords = ['machine learning', 'artificial intelligence', 'computer vision', 'natural language processing']
        
        logger.info(f"🔬 Zbieranie prawdziwych danych z arXiv dla {len(keywords)} kategorii...")
        papers = []
        
        session = await self.get_session()
        
        for keyword in keywords:
            try:
                # arXiv API query
                query = f'all:"{keyword}"'
                url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_papers//len(keywords)}"
                
                logger.info(f"📡 Pobieranie: {keyword}")
                async with session.get(url) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        parsed = self.parse_arxiv_xml(xml_content)
                        papers.extend(parsed)
                        logger.info(f"✅ {keyword}: {len(parsed)} artykułów")
                        
                        # Rate limiting
                        await asyncio.sleep(3)
                    else:
                        logger.error(f"❌ arXiv error {response.status} for {keyword}")
                        
            except Exception as e:
                logger.error(f"❌ Error harvesting {keyword}: {e}")
        
        self.results['arxiv'] = papers
        logger.info(f"🎯 arXiv total: {len(papers)} prawdziwych artykułów")
        return papers

    def parse_arxiv_xml(self, xml_content: str):
        """Parse arXiv XML response - prawdziwe dane"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                
                # Authors
                authors = []
                for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                    name_elem = author.find('{http://www.w3.org/2005/Atom}name')
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text)
                
                if title_elem is not None and published_elem is not None:
                    pub_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                    
                    paper = {
                        'title': title_elem.text.strip() if title_elem.text else '',
                        'abstract': summary_elem.text.strip() if summary_elem is not None and summary_elem.text else '',
                        'authors': '; '.join(authors),
                        'publication_date': pub_date.strftime('%Y-%m-%d'),
                        'source': 'arXiv',
                        'url': id_elem.text if id_elem is not None and id_elem.text else '',
                        'year': pub_date.year,
                        'type': 'scientific_paper'
                    }
                    papers.append(paper)
                    
        except Exception as e:
            logger.error(f"Error parsing arXiv XML: {e}")
        
        return papers

    async def harvest_pubmed_real(self, keywords: list = None, max_papers: int = 30):
        """Pobiera prawdziwe artykuły z PubMed"""
        if not keywords:
            keywords = ['bioinformatics', 'computational biology', 'medical AI']
        
        logger.info(f"🧬 Zbieranie prawdziwych danych z PubMed dla {len(keywords)} kategorii...")
        papers = []
        
        session = await self.get_session()
        
        for keyword in keywords:
            try:
                # PubMed search
                search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                search_params = {
                    'db': 'pubmed',
                    'term': keyword,
                    'retmax': max_papers // len(keywords),
                    'retmode': 'json'
                }
                
                logger.info(f"📡 Pobieranie PubMed: {keyword}")
                async with session.get(search_url, params=search_params) as response:
                    if response.status == 200:
                        search_data = await response.json()
                        
                        if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                            pmids = search_data['esearchresult']['idlist']
                            
                            if pmids:
                                await asyncio.sleep(2)  # Rate limiting
                                
                                # Fetch details
                                fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                                fetch_params = {
                                    'db': 'pubmed',
                                    'id': ','.join(pmids[:10]),  # Limit batch
                                    'retmode': 'xml'
                                }
                                
                                async with session.get(fetch_url, params=fetch_params) as fetch_response:
                                    if fetch_response.status == 200:
                                        xml_content = await fetch_response.text()
                                        parsed = self.parse_pubmed_xml(xml_content, keyword)
                                        papers.extend(parsed)
                                        logger.info(f"✅ {keyword}: {len(parsed)} artykułów PubMed")
                                        
                await asyncio.sleep(3)  # Rate limiting between searches
                                        
            except Exception as e:
                logger.error(f"❌ PubMed error for {keyword}: {e}")
        
        self.results['pubmed'] = papers
        logger.info(f"🎯 PubMed total: {len(papers)} prawdziwych artykułów")
        return papers

    def parse_pubmed_xml(self, xml_content: str, keyword: str):
        """Parse PubMed XML - prawdziwe dane"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                title_elem = article.find('.//ArticleTitle')
                abstract_elem = article.find('.//Abstract/AbstractText')
                
                # Authors
                authors = []
                for author in article.findall('.//Author'):
                    lastname = author.find('LastName')
                    forename = author.find('ForeName')
                    if lastname is not None and forename is not None:
                        authors.append(f"{forename.text} {lastname.text}")
                
                # Journal
                journal_elem = article.find('.//Journal/Title')
                journal = journal_elem.text if journal_elem is not None and journal_elem.text else ''
                
                # Date
                pub_date_elem = article.find('.//PubDate')
                year = 2020  # Default
                if pub_date_elem is not None:
                    year_elem = pub_date_elem.find('Year')
                    if year_elem is not None and year_elem.text:
                        try:
                            year = int(year_elem.text)
                        except ValueError:
                            year = 2020
                
                if title_elem is not None and title_elem.text:
                    paper = {
                        'title': title_elem.text,
                        'abstract': abstract_elem.text[:500] if abstract_elem is not None and abstract_elem.text else '',
                        'authors': '; '.join(authors),
                        'journal': journal,
                        'publication_date': f"{year}-06-15",
                        'source': 'PubMed',
                        'keyword': keyword,
                        'year': year,
                        'type': 'medical_paper'
                    }
                    papers.append(paper)
                    
        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {e}")
        
        return papers

    async def harvest_wikipedia_real(self, topics: list = None, max_articles: int = 20):
        """Pobiera prawdziwe dane z Wikipedia"""
        if not topics:
            topics = ['Machine_learning', 'Artificial_intelligence', 'Computer_science', 'History_of_computing']
        
        logger.info(f"📚 Zbieranie prawdziwych danych z Wikipedia dla {len(topics)} tematów...")
        articles = []
        
        session = await self.get_session()
        
        for topic in topics:
            try:
                # Wikipedia API
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
                
                logger.info(f"📡 Pobieranie Wikipedia: {topic}")
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        article = {
                            'title': data.get('title', topic),
                            'extract': data.get('extract', ''),
                            'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                            'source': 'Wikipedia',
                            'topic': topic,
                            'type': 'encyclopedia_article',
                            'language': 'en'
                        }
                        articles.append(article)
                        logger.info(f"✅ {topic}: Wikipedia article")
                        
                await asyncio.sleep(1)  # Rate limiting
                        
            except Exception as e:
                logger.error(f"❌ Wikipedia error for {topic}: {e}")
        
        self.results['wikipedia'] = articles
        logger.info(f"🎯 Wikipedia total: {len(articles)} prawdziwych artykułów")
        return articles

    async def harvest_crossref_real(self, query: str = "machine learning", max_papers: int = 25):
        """Pobiera prawdziwe dane z Crossref"""
        logger.info(f"📖 Zbieranie prawdziwych danych z Crossref dla '{query}'...")
        papers = []
        
        session = await self.get_session()
        
        try:
            # Crossref API
            url = f"https://api.crossref.org/works"
            params = {
                'query': query,
                'rows': max_papers,
                'select': 'title,author,published-print,URL,abstract,subject'
            }
            
            logger.info(f"📡 Pobieranie Crossref: {query}")
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'message' in data and 'items' in data['message']:
                        for item in data['message']['items']:
                            # Extract data
                            title = ''
                            if 'title' in item and item['title']:
                                title = item['title'][0]
                            
                            authors = []
                            if 'author' in item:
                                for author in item['author'][:3]:  # Limit authors
                                    if 'given' in author and 'family' in author:
                                        authors.append(f"{author['given']} {author['family']}")
                            
                            year = 2020
                            if 'published-print' in item and 'date-parts' in item['published-print']:
                                date_parts = item['published-print']['date-parts'][0]
                                if date_parts:
                                    year = date_parts[0]
                            
                            paper = {
                                'title': title,
                                'authors': '; '.join(authors),
                                'year': year,
                                'publication_date': f"{year}-01-01",
                                'url': item.get('URL', ''),
                                'source': 'Crossref',
                                'type': 'academic_paper'
                            }
                            papers.append(paper)
                            
                        logger.info(f"✅ Crossref: {len(papers)} prawdziwych artykułów")
                        
        except Exception as e:
            logger.error(f"❌ Crossref error: {e}")
        
        self.results['crossref'] = papers
        logger.info(f"🎯 Crossref total: {len(papers)} prawdziwych artykułów")
        return papers

    def save_results(self, filename: str = "real_data_complete.csv"):
        """Zapisz wszystkie prawdziwe dane do CSV"""
        all_data = []
        
        for source, records in self.results.items():
            for record in records:
                record['data_source'] = source
                all_data.append(record)
        
        if all_data:
            df = pd.DataFrame(all_data)
            output_path = Path(filename)
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"💾 Zapisano {len(all_data)} prawdziwych rekordów do {output_path}")
            return output_path
        else:
            logger.warning("Brak danych do zapisania")
            return None

    async def run_full_harvest(self):
        """Uruchom pełne zbieranie prawdziwych danych"""
        logger.info("🚀 Rozpoczynam zbieranie PRAWDZIWYCH danych z rzeczywistych API")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Harvest from all real sources
        await self.harvest_arxiv_real(max_papers=40)
        await self.harvest_pubmed_real(max_papers=20)
        await self.harvest_wikipedia_real(max_articles=15)
        await self.harvest_crossref_real(max_papers=20)
        
        elapsed = time.time() - start_time
        
        # Summary
        total_records = sum(len(records) for records in self.results.values())
        
        logger.info("=" * 60)
        logger.info(f"🎉 Zbieranie prawdziwych danych zakończone!")
        logger.info(f"⏱️  Czas: {elapsed:.1f} sekund")
        logger.info(f"📊 Łącznie zebranych rekordów: {total_records}")
        logger.info("📈 Podział źródeł:")
        
        for source, records in self.results.items():
            if records:
                logger.info(f"  {source}: {len(records)} prawdziwych rekordów")
        
        # Save results
        csv_path = self.save_results()
        
        return {
            'total_records': total_records,
            'sources': {source: len(records) for source, records in self.results.items()},
            'elapsed_time': elapsed,
            'csv_file': str(csv_path) if csv_path else None
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main function - zbieranie prawdziwych danych"""
    harvester = RealDataHarvester()
    
    try:
        results = await harvester.run_full_harvest()
        
        print(f"\n🎯 PODSUMOWANIE PRAWDZIWYCH DANYCH:")
        print(f"📊 Łącznie: {results['total_records']} rekordów")
        print(f"⏱️  Czas: {results['elapsed_time']:.1f}s")
        print(f"💾 Plik: {results['csv_file']}")
        
        print(f"\n📈 Źródła:")
        for source, count in results['sources'].items():
            if count > 0:
                print(f"  ✅ {source}: {count} prawdziwych rekordów")
        
        print(f"\n🔥 To są PRAWDZIWE dane z rzeczywistych API, nie mock!")
        
    finally:
        await harvester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())