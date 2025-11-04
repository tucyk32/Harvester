#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
astro_historical_pattern_analyzer.py
-----------------------------------
Analiza wzorców między zdarzeniami astronomicznymi a historycznymi
"""

import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AstroHistoricalPatternAnalyzer:
    def __init__(self):
        self.astronomical_data = None
        self.historical_data = None
        self.combined_analysis = None

    def load_astronomical_sample(self, max_events=5000):
        """Ładuje próbkę danych astronomicznych"""
        logger.info(f"🌌 LOADING ASTRONOMICAL SAMPLE (max {max_events})!")

        events = []

        # Load from available files
        files_to_check = [
            'astronomical_współczesność.json',
            'astronomical_wiek_xix.json'
        ]

        for file_name in files_to_check:
            if Path(file_name).exists():
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    results = data.get('results', {})
                    for epoch_key, epoch_events in results.items():
                        if isinstance(epoch_events, list):
                            events.extend(epoch_events[:max_events//2])

                    if len(events) >= max_events:
                        break
                except Exception as e:
                    logger.error(f"❌ Error loading {file_name}: {e}")

        events = events[:max_events]
        df = pd.DataFrame(events)

        # Prepare data
        df['year'] = pd.to_numeric(df.get('year'), errors='coerce')
        df['date'] = pd.to_datetime(df.get('date'), errors='coerce')
        df['event_type'] = 'astronomical'

        self.astronomical_data = df
        logger.info(f"✅ Loaded {len(df)} astronomical events")
        return df

    def load_historical_sample(self, max_events=10000):
        """Ładuje próbkę danych historycznych"""
        logger.info(f"📜 LOADING HISTORICAL SAMPLE (max {max_events})!")

        try:
            # Load historical data in chunks to handle large file
            historical_events = []

            with open('MEGA_WORLD_CHRONOLOGY.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract events from the structure
            if isinstance(data, list):
                events = data
            elif isinstance(data, dict) and 'events' in data:
                events = data['events']
            else:
                events = []

            # Sample events
            import random
            if len(events) > max_events:
                events = random.sample(events, max_events)

            for event in events:
                if isinstance(event, dict):
                    historical_events.append({
                        'title': event.get('title', ''),
                        'year': event.get('year', None),
                        'category': event.get('category', 'historical'),
                        'event_type': 'historical'
                    })

            df = pd.DataFrame(historical_events)
            df['year'] = pd.to_numeric(df['year'], errors='coerce')

            self.historical_data = df
            logger.info(f"✅ Loaded {len(df)} historical events")
            return df

        except Exception as e:
            logger.error(f"❌ Error loading historical data: {e}")
            return pd.DataFrame()

    def combine_datasets(self):
        """Łączy dane astronomiczne z historycznymi"""
        logger.info("🔗 COMBINING ASTRO-HISTORICAL DATASETS!")

        if self.astronomical_data is None:
            logger.error("No astronomical data!")
            return

        astro_df = self.astronomical_data.copy()
        hist_df = self.historical_data.copy() if self.historical_data is not None else pd.DataFrame()

        # Combine
        combined = pd.concat([astro_df, hist_df], ignore_index=True)
        combined['decade'] = (combined['year'] // 10) * 10

        self.combined_analysis = combined
        logger.info(f"🎯 Combined dataset: {len(combined)} events")
        return combined

    def analyze_temporal_patterns(self):
        """Analizuje wzorce temporalne"""
        logger.info("⏰ ANALYZING TEMPORAL PATTERNS!")

        if self.combined_analysis is None:
            return

        df = self.combined_analysis.copy()

        # Events by decade and type
        decade_patterns = df.groupby(['decade', 'event_type']).size().unstack(fill_value=0)

        # Calculate ratios and correlations
        if len(decade_patterns.columns) >= 2:
            astro_col = 'astronomical' if 'astronomical' in decade_patterns.columns else decade_patterns.columns[0]
            hist_col = 'historical' if 'historical' in decade_patterns.columns else decade_patterns.columns[1]

            # Correlation between astronomical and historical events
            correlation = decade_patterns[astro_col].corr(decade_patterns[hist_col])

            logger.info(f"📈 Astro-Historical Correlation: {correlation:.3f}")

            # Peak periods
            astro_peaks = decade_patterns[astro_col].nlargest(3)
            hist_peaks = decade_patterns[hist_col].nlargest(3)

            logger.info("🌟 Astronomical Peak Decades:")
            for decade, count in astro_peaks.items():
                logger.info(f"   {decade}s: {count} events")

            logger.info("📜 Historical Peak Decades:")
            for decade, count in hist_peaks.items():
                logger.info(f"   {decade}s: {count} events")

        return decade_patterns

    def analyze_category_correlations(self):
        """Analizuje korelacje między kategoriami"""
        logger.info("🏷️ ANALYZING CATEGORY CORRELATIONS!")

        if self.combined_analysis is None:
            return

        df = self.combined_analysis.copy()

        # Category distributions
        astro_categories = df[df['event_type'] == 'astronomical']['subcategory'].value_counts()
        hist_categories = df[df['event_type'] == 'historical']['category'].value_counts()

        logger.info("🌌 Astronomical Categories:")
        for cat, count in astro_categories.head(5).items():
            logger.info(f"   {cat}: {count}")

        logger.info("📜 Historical Categories:")
        for cat, count in hist_categories.head(5).items():
            logger.info(f"   {cat}: {count}")

        return {
            'astronomical_categories': astro_categories.to_dict(),
            'historical_categories': hist_categories.to_dict()
        }

    def create_visualizations(self):
        """Tworzy wizualizacje wzorców"""
        logger.info("📊 CREATING PATTERN VISUALIZATIONS!")

        if self.combined_analysis is None or len(self.combined_analysis) == 0:
            logger.warning("No data for visualization")
            return

        df = self.combined_analysis.copy()

        try:
            # Set up the plotting style
            plt.style.use('default')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Astro-Historical Pattern Analysis', fontsize=16)

            # 1. Events by decade
            decade_counts = df.groupby(['decade', 'event_type']).size().unstack(fill_value=0)

            # Ensure we have numeric data
            decade_counts = decade_counts.select_dtypes(include=[np.number])

            if not decade_counts.empty:
                decade_counts.plot(kind='bar', ax=axes[0,0])
                axes[0,0].set_title('Events by Decade and Type')
                axes[0,0].set_xlabel('Decade')
                axes[0,0].set_ylabel('Number of Events')
                axes[0,0].tick_params(axis='x', rotation=45)
            else:
                axes[0,0].text(0.5, 0.5, 'No numeric data available', ha='center', va='center')
                axes[0,0].set_title('Events by Decade and Type (No Data)')

            # 2. Astronomical events distribution
            if 'subcategory' in df.columns and len(df[df['event_type'] == 'astronomical']) > 0:
                astro_cats = df[df['event_type'] == 'astronomical']['subcategory'].value_counts().head(10)
                if not astro_cats.empty:
                    astro_cats.plot(kind='pie', ax=axes[0,1], autopct='%1.1f%%')
                    axes[0,1].set_title('Astronomical Event Categories')
                else:
                    axes[0,1].text(0.5, 0.5, 'No astronomical data', ha='center', va='center')
                    axes[0,1].set_title('Astronomical Event Categories (No Data)')

            # 3. Historical events distribution
            if len(df[df['event_type'] == 'historical']) > 0:
                hist_cats = df[df['event_type'] == 'historical']['category'].value_counts().head(10)
                if not hist_cats.empty:
                    hist_cats.plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%')
                    axes[1,0].set_title('Historical Event Categories')
                else:
                    axes[1,0].text(0.5, 0.5, 'No historical data', ha='center', va='center')
                    axes[1,0].set_title('Historical Event Categories (No Data)')

            # 4. Timeline correlation
            if not decade_counts.empty and len(decade_counts.columns) >= 2:
                ax4 = axes[1,1]
                for col in decade_counts.columns:
                    ax4.plot(decade_counts.index, decade_counts[col], label=col, marker='o')
                ax4.set_title('Astro-Historical Timeline Correlation')
                ax4.set_xlabel('Decade')
                ax4.set_ylabel('Number of Events')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                axes[1,1].text(0.5, 0.5, 'Insufficient data for correlation', ha='center', va='center')
                axes[1,1].set_title('Timeline Correlation (Insufficient Data)')

            plt.tight_layout()
            plt.savefig('astro_historical_patterns.png', dpi=300, bbox_inches='tight')
            logger.info("💾 Visualization saved to astro_historical_patterns.png")

            return 'astro_historical_patterns.png'

        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return

    def generate_pattern_report(self):
        """Generuje raport z analizy wzorców"""
        logger.info("📋 GENERATING PATTERN ANALYSIS REPORT!")

        report = {
            'generated_at': datetime.now().isoformat(),
            'analysis_type': 'astro_historical_patterns',
            'data_summary': {
                'astronomical_events': len(self.astronomical_data) if self.astronomical_data is not None else 0,
                'historical_events': len(self.historical_data) if self.historical_data is not None else 0,
                'total_events': len(self.combined_analysis) if self.combined_analysis is not None else 0
            },
            'temporal_patterns': {},
            'category_analysis': {},
            'key_findings': [],
            'visualizations': []
        }

        # Temporal patterns
        temporal_data = self.analyze_temporal_patterns()
        if temporal_data is not None:
            report['temporal_patterns'] = {
                'decade_distribution': temporal_data.to_dict(),
                'correlation_coefficient': temporal_data.corr().iloc[0,1] if len(temporal_data.columns) >= 2 else None
            }

        # Category analysis
        category_data = self.analyze_category_correlations()
        if category_data:
            report['category_analysis'] = category_data

        # Key findings
        report['key_findings'] = [
            "Analysis of astronomical and historical event patterns",
            "Temporal correlation between astronomical and historical events",
            "Category distributions across different time periods",
            "Peak activity periods identified for both event types",
            "Visual patterns created for better understanding"
        ]

        # Create visualizations
        viz_file = self.create_visualizations()
        if viz_file:
            report['visualizations'].append(viz_file)

        with open('astro_historical_patterns.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info("💾 Pattern report saved to astro_historical_patterns.json")
        return report

    def run_pattern_analysis(self):
        """Uruchamia kompletną analizę wzorców"""
        logger.info("🔍🕰️ STARTING ASTRO-HISTORICAL PATTERN ANALYSIS!")

        try:
            # Load data
            self.load_astronomical_sample(max_events=3000)
            self.load_historical_sample(max_events=5000)

            # Combine and analyze
            self.combine_datasets()
            self.analyze_temporal_patterns()
            self.analyze_category_correlations()

            # Generate report
            report = self.generate_pattern_report()

            logger.info("🎉🔍 PATTERN ANALYSIS COMPLETED!")
            logger.info(f"📊 Total events analyzed: {report['data_summary']['total_events']}")

            return report

        except Exception as e:
            logger.error(f"💥 ERROR in pattern analysis: {e}")
            raise

def main():
    print("🔍🕰️ ASTRO-HISTORICAL PATTERN ANALYZER!")
    print("Analiza wzorców między zdarzeniami astronomicznymi a historycznymi")

    analyzer = AstroHistoricalPatternAnalyzer()
    report = analyzer.run_pattern_analysis()

    print("\n📊 PATTERN ANALYSIS RESULTS:")
    print(f"Astronomical events: {report['data_summary']['astronomical_events']}")
    print(f"Historical events: {report['data_summary']['historical_events']}")
    print(f"Total events: {report['data_summary']['total_events']}")

    if 'temporal_patterns' in report and report['temporal_patterns'].get('correlation_coefficient'):
        print(f"📈 Correlation coefficient: {report['temporal_patterns']['correlation_coefficient']:.3f}")

    print("\n🔍 KEY FINDINGS:")
    for finding in report['key_findings'][:3]:
        print(f"  ✅ {finding}")

    print(f"\n💾 Full report saved to: astro_historical_patterns.json")
    if report['visualizations']:
        print(f"📊 Visualizations: {', '.join(report['visualizations'])}")

if __name__ == "__main__":
    main()