#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_harvested_data.py
-------------------------
Analiza zebranych danych z wszystkich harvesterów
"""

import pandas as pd
import json
from pathlib import Path

def analyze_advanced_harvester():
    """Analiza Advanced Data Harvester"""
    print("🔍 === ADVANCED DATA HARVESTER ANALYSIS ===")
    try:
        # Try different possible file locations
        possible_files = [
            'cache/harvested_data.csv',
            'data/harvested_data.csv', 
            'harvested_data.csv',
            'advanced_harvested_data.csv'
        ]
        
        df = None
        for file_path in possible_files:
            try:
            df = pd.read_csv(file_path)
            print(f"✅ Found data file: {file_path}")
            break
            except FileNotFoundError:
            continue
        
        if df is None:
            print("❌ No Advanced harvester data file found")
            return
        print(f"📊 Total records: {len(df)}")
        
        print("\n📈 Source distribution:")
        print(df['source'].value_counts())
        
        print("\n🌍 Language distribution:")
        print(df['language'].value_counts())
        
        print("\n📅 Year range:")
        print(f"From {df['year_abs'].min()} to {df['year_abs'].max()}")
        
        print("\n🏷️ Category distribution:")
        print(df['category'].value_counts())
        
        print(f"\n📄 Sample record:")
        sample = df.iloc[100]
        print(f"Title: {sample['title'][:100]}...")
        print(f"Source: {sample['source']}")
        print(f"Year: {sample['year_abs']}")
        print(f"Language: {sample['language']}")
        
    except Exception as e:
        print(f"❌ Error analyzing Advanced harvester: {e}")

def analyze_real_harvester():
    """Analiza Real Data Harvester"""
    print("\n🔬 === REAL DATA HARVESTER ANALYSIS ===")
    try:
        df = pd.read_csv('real_data_complete.csv')
        print(f"📊 Total records: {len(df)}")
        
        print("\n📈 Data source distribution:")
        print(df['data_source'].value_counts())
        
        print("\n📝 Type distribution:")
        print(df['type'].value_counts())
        
        print("\n📅 Year range:")
        print(f"From {df['year'].min()} to {df['year'].max()}")
        
        print(f"\n📄 Sample arXiv paper:")
        arxiv_papers = df[df['data_source'] == 'arxiv']
        if len(arxiv_papers) > 0:
            sample = arxiv_papers.iloc[0]
            print(f"Title: {sample['title']}")
            print(f"Authors: {sample['authors']}")
            print(f"Year: {sample['year']}")
            print(f"Abstract: {sample['abstract'][:200]}...")
        
        print(f"\n📄 Sample PubMed paper:")
        pubmed_papers = df[df['data_source'] == 'pubmed']
        if len(pubmed_papers) > 0:
            sample = pubmed_papers.iloc[0]
            print(f"Title: {sample['title']}")
            print(f"Journal: {sample.get('journal', 'N/A')}")
            print(f"Year: {sample['year']}")
        
    except Exception as e:
        print(f"❌ Error analyzing Real harvester: {e}")

def analyze_scientific_archives():
    """Analiza Scientific Archives JSON files"""
    print("\n📚 === SCIENTIFIC ARCHIVES ANALYSIS ===")
    
    json_files = [
        'scientific_papers_machine_learning_history.json',
        'scientific_papers_artificial_intelligence_timeline.json',
        'scientific_papers_computer_science_evolution.json'
    ]
    
    total_papers = 0
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                papers_count = data['metadata']['total_papers']
                total_papers += papers_count
                print(f"📄 {file}: {papers_count} papers")
                
                # Sample paper
                if 'results' in data and 'timeline_events' in data['results']:
                    events = data['results']['timeline_events']
                    if events:
                        sample = events[0]
                        print(f"  Sample: {sample['title'][:60]}...")
                        print(f"  Authors: {', '.join(sample['authors'][:2])}...")
                        print(f"  Year: {sample['year']}")
                        
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
    
    print(f"\n📊 Total Scientific Archives papers: {total_papers}")

def analyze_ml_datasets():
    """Analiza ML datasets"""
    print("\n🤖 === ML DATASETS ANALYSIS ===")
    
    datasets = [
        'unified_output/ml_complete_dataset.csv',
        'unified_output/ml_high_confidence_dataset.csv',
        'unified_output/ml_timeseries_dataset.csv',
        'unified_output/ml_features_dataset.csv'
    ]
    
    for dataset_path in datasets:
        try:
            df = pd.read_csv(dataset_path)
            dataset_name = Path(dataset_path).stem
            print(f"\n📊 {dataset_name}:")
            print(f"  Records: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Source types: {df['source_type'].value_counts().to_dict()}")
            
            if 'confidence_score' in df.columns:
                print(f"  Avg confidence: {df['confidence_score'].mean():.3f}")
            
            if 'year_abs' in df.columns:
                print(f"  Year range: {df['year_abs'].min()} to {df['year_abs'].max()}")
                
        except Exception as e:
            print(f"❌ Error analyzing {dataset_path}: {e}")

def analyze_ssl_fixed():
    """Analiza SSL Fixed Harvester"""
    print("\n🔐 === SSL FIXED HARVESTER ANALYSIS ===")
    try:
        df = pd.read_csv('real_harvested_data.csv')
        print(f"📊 Total records: {len(df)}")
        
        print("\n📈 Source distribution:")
        print(df['source_database'].value_counts())
        
        print("\n📅 Year range:")
        print(f"From {df['year_abs'].min()} to {df['year_abs'].max()}")
        
        print(f"\n📄 Sample arXiv paper:")
        arxiv_papers = df[df['source_database'] == 'arxiv']
        if len(arxiv_papers) > 0:
            sample = arxiv_papers.iloc[0]
            print(f"Title: {sample['title'][:100]}...")
            print(f"Year: {sample['year_abs']}")
            print(f"Abstract: {sample['abstract'][:150]}...")
        
    except Exception as e:
        print(f"❌ Error analyzing SSL Fixed harvester: {e}")

def main():
    """Main analysis function"""
    print("🔍 COMPREHENSIVE DATA ANALYSIS")
    print("=" * 50)
    
    analyze_advanced_harvester()
    analyze_real_harvester()
    analyze_scientific_archives()
    analyze_ssl_fixed()
    analyze_ml_datasets()
    
    print("\n" + "=" * 50)
    print("✅ ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()