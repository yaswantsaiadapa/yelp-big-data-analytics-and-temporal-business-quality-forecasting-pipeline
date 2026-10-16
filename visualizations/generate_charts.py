import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#EEEEEE'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, 'results', 'exported')
VIZ_DIR = os.path.join(BASE_DIR, 'visualizations')
os.makedirs(VIZ_DIR, exist_ok=True)

def plot_rating_distribution():
    path = os.path.join(EXPORT_DIR, 'hive', 'rating_distribution', '000000_0')
    df = pd.read_csv(path, sep='\t', header=None, names=['stars', 'count'])
    df['stars'] = df['stars'].astype(float)
    df = df.sort_values('stars')
    total = df['count'].sum()
    df['percentage'] = (df['count'] / total) * 100

    plt.figure(figsize=(9, 5.5), dpi=300)
    colors = sns.color_palette("Blues_d", len(df))
    bars = plt.bar(df['stars'].astype(str), df['count'], color=colors, edgecolor='#1d3557', width=0.65)
    
    plt.title('Distribution of Yelp Business Star Ratings (N = 150,346)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Star Rating (Stars)', fontsize=11, labelpad=10)
    plt.ylabel('Number of Businesses', fontsize=11, labelpad=10)
    plt.grid(axis='y', alpha=0.7)
    
    for bar, pct, cnt in zip(bars, df['percentage'], df['count']):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 500, f'{cnt:,.0f}\n({pct:.1f}%)', 
                 ha='center', va='bottom', fontsize=9, fontweight='semibold', color='#1d3557')

    plt.ylim(0, max(df['count']) * 1.18)
    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '01_rating_distribution.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_state_business_distribution():
    path = os.path.join(EXPORT_DIR, 'hive', 'businesses_by_state', '000000_0')
    df = pd.read_csv(path, sep='\t', header=None, names=['state', 'count'])
    top_df = df.head(12).copy()
    top_df = top_df.sort_values('count', ascending=True)

    plt.figure(figsize=(10, 6), dpi=300)
    palette = sns.color_palette("mako", len(top_df))
    bars = plt.barh(top_df['state'], top_df['count'], color=palette, edgecolor='#2b2d42', height=0.68)
    
    plt.title('Top Geographic Regions by Yelp Business Presence', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Number of Registered Businesses', fontsize=11, labelpad=10)
    plt.ylabel('State / Region Code', fontsize=11, labelpad=10)
    plt.grid(axis='x', alpha=0.7)

    for bar in bars:
        w = bar.get_width()
        plt.text(w + 400, bar.get_y() + bar.get_height()/2.0, f'{w:,.0f}', 
                 ha='left', va='center', fontsize=9.5, fontweight='semibold', color='#2b2d42')

    plt.xlim(0, max(top_df['count']) * 1.15)
    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '02_state_business_distribution.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_avg_rating_by_state():
    path = os.path.join(EXPORT_DIR, 'hive', 'avg_rating_by_state', '000000_0')
    df = pd.read_csv(path, sep='\t', header=None, names=['state', 'avg_rating', 'count'])
    df = df.sort_values('avg_rating', ascending=True)

    plt.figure(figsize=(10, 6), dpi=300)
    norm = plt.Normalize(df['avg_rating'].min() - 0.2, df['avg_rating'].max() + 0.1)
    colors = plt.cm.viridis(norm(df['avg_rating']))
    
    bars = plt.barh(df['state'], df['avg_rating'], color=colors, edgecolor='#333333', height=0.65)
    
    overall_mean = df['avg_rating'].mean()
    plt.axvline(overall_mean, color='#e63946', linestyle='--', linewidth=1.5, 
                label=f'Cross-State Mean: {overall_mean:.2f}')

    plt.title('Average Business Star Rating Across Major States (Min 100 Businesses)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Average Star Rating (Scale 1.0 - 5.0)', fontsize=11, labelpad=10)
    plt.ylabel('State Code', fontsize=11, labelpad=10)
    plt.xlim(3.0, 4.25)
    plt.grid(axis='x', alpha=0.7)
    plt.legend(loc='lower right', frameon=True)

    for bar, val in zip(bars, df['avg_rating']):
        w = bar.get_width()
        plt.text(w + 0.02, bar.get_y() + bar.get_height()/2.0, f'{val:.2f}', 
                 ha='left', va='center', fontsize=9.5, fontweight='bold', color='#1d3557')

    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '03_state_avg_rating_comparison.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_state_review_vs_rating():
    path = os.path.join(EXPORT_DIR, 'hive', 'reviews_by_state', '000000_0')
    df = pd.read_csv(path, sep='\t', header=None, names=['state', 'review_count', 'avg_rating'])
    df = df[df['review_count'] >= 50000].sort_values('review_count', ascending=False)

    fig, ax1 = plt.subplots(figsize=(11, 6), dpi=300)
    
    x = np.arange(len(df))
    width = 0.55

    color1 = '#3a86ff'
    bars = ax1.bar(x, df['review_count'] / 1e6, width=width, color=color1, alpha=0.85, label='Total Reviews (Millions)', edgecolor='#023e8a')
    ax1.set_xlabel('State Code', fontsize=12, labelpad=10)
    ax1.set_ylabel('Review Volume (Millions)', color='#023e8a', fontsize=12, labelpad=10)
    ax1.tick_params(axis='y', labelcolor='#023e8a')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['state'], fontsize=10, fontweight='bold')
    ax1.grid(axis='y', alpha=0.5)

    ax2 = ax1.twinx()
    color2 = '#d90429'
    line = ax2.plot(x, df['avg_rating'], color=color2, marker='o', linewidth=2.5, markersize=7, label='Average Review Rating')
    ax2.set_ylabel('Average Rating (Stars)', color=color2, fontsize=12, labelpad=10)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(3.2, 4.2)

    for i, txt in enumerate(df['avg_rating']):
        ax2.annotate(f'{txt:.2f}', (x[i], df['avg_rating'].iloc[i] + 0.04), ha='center', fontsize=9, fontweight='bold', color=color2)

    plt.title('State-Level Review Volume vs. Mean Customer Review Rating', fontsize=14, fontweight='bold', pad=15)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True)

    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '04_state_review_volume_vs_rating.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_top_categories():
    path = os.path.join(EXPORT_DIR, 'hive', 'top_categories', '000000_0')
    df = pd.read_csv(path, sep='\t', header=None, names=['category', 'count'])
    top_df = df.head(15).sort_values('count', ascending=True)

    plt.figure(figsize=(10.5, 6.5), dpi=300)
    palette = sns.color_palette("Spectral", len(top_df))
    bars = plt.barh(top_df['category'], top_df['count'], color=palette, edgecolor='#333333', height=0.68)
    
    plt.title('Top 15 Most Prevalent Business Categories on Yelp', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Business Count', fontsize=11, labelpad=10)
    plt.ylabel('Category', fontsize=11, labelpad=10)
    plt.grid(axis='x', alpha=0.7)

    for bar in bars:
        w = bar.get_width()
        plt.text(w + 500, bar.get_y() + bar.get_height()/2.0, f'{w:,.0f}', 
                 ha='left', va='center', fontsize=9, fontweight='semibold', color='#2b2d42')

    plt.xlim(0, max(top_df['count']) * 1.15)
    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '05_top_business_categories.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_aspect_mentions():
    path = os.path.join(EXPORT_DIR, 'spark_business_quality', 'aspect_summary', 'part-00000-ee768ba4-4535-448e-a168-ac93d928f031-c000.csv')
    df = pd.read_csv(path)
    df['aspect_clean'] = df['aspect'].str.replace('_', ' ').str.title()
    df = df.sort_values('total_mentions', ascending=True)
    df['mentions_millions'] = df['total_mentions'] / 1e6

    plt.figure(figsize=(10, 5.5), dpi=300)
    palette = sns.color_palette("flare", len(df))
    bars = plt.barh(df['aspect_clean'], df['mentions_millions'], color=palette, edgecolor='#2b2d42', height=0.65)
    
    plt.title('Aspect-Based Sentiment Scope: Customer Discussion Frequency (Spark NLP)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Total Review Mentions (in Millions)', fontsize=11, labelpad=10)
    plt.ylabel('Business Quality Aspect Dimension', fontsize=11, labelpad=10)
    plt.grid(axis='x', alpha=0.7)

    for bar, raw in zip(bars, df['total_mentions']):
        w = bar.get_width()
        plt.text(w + 0.05, bar.get_y() + bar.get_height()/2.0, f'{w:.2f}M ({raw:,.0f})', 
                 ha='left', va='center', fontsize=9.5, fontweight='bold', color='#1d3557')

    plt.xlim(0, max(df['mentions_millions']) * 1.25)
    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '06_aspect_mentions_breakdown.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_confusion_matrix():
    path = os.path.join(EXPORT_DIR, 'spark_quality_prediction', 'confusion_matrix', 'part-00000-ae3b64a9-9ec2-4eb6-b5d4-f85c3720d315-c000.csv')
    df = pd.read_csv(path)
    pivot_df = df.pivot(index='actual_label', columns='predicted_label', values='count')
    classes = ['Declining', 'Stable', 'Improving']
    pivot_df = pivot_df.reindex(index=classes, columns=classes)

    pivot_norm = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    sns.heatmap(pivot_df, annot=True, fmt=',d', cmap='Blues', cbar=False, ax=ax1,
                annot_kws={'size': 12, 'weight': 'bold'}, linewidths=1.5, linecolor='white')
    ax1.set_title('Confusion Matrix (Raw Counts)', fontsize=13, fontweight='bold', pad=12)
    ax1.set_xlabel('Predicted Quality Trajectory', fontsize=11, labelpad=8)
    ax1.set_ylabel('Actual Future Trajectory', fontsize=11, labelpad=8)

    sns.heatmap(pivot_norm, annot=True, fmt='.1f', cmap='Blues', cbar=True, ax=ax2,
                annot_kws={'size': 12, 'weight': 'bold'}, linewidths=1.5, linecolor='white')
    ax2.set_title('Normalized Recall Matrix (% of Actual)', fontsize=13, fontweight='bold', pad=12)
    ax2.set_xlabel('Predicted Quality Trajectory', fontsize=11, labelpad=8)
    ax2.set_ylabel('Actual Future Trajectory', fontsize=11, labelpad=8)

    plt.suptitle('Temporal Business Quality Prediction Evaluation (Random Forest Classifier)', 
                 fontsize=15, fontweight='bold', y=1.03)
    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '07_confusion_matrix_heatmap.png')
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")

def plot_model_metrics():
    path = os.path.join(EXPORT_DIR, 'spark_quality_prediction', 'metrics', 'part-00000-d437e33e-6c6b-42c3-800e-e9f6cd3094b5-c000.csv')
    df = pd.read_csv(path)
    
    metric_map = {
        'accuracy': 'Accuracy',
        'weightedPrecision': 'Weighted Precision',
        'weightedRecall': 'Weighted Recall',
        'f1': 'F1 Score'
    }
    df['metric_name'] = df['metric'].map(metric_map)
    df['percentage'] = df['value'] * 100

    plt.figure(figsize=(8.5, 5), dpi=300)
    colors = ['#2a9d8f', '#457b9d', '#1d3557', '#e76f51']
    bars = plt.bar(df['metric_name'], df['percentage'], color=colors, edgecolor='#1d3557', width=0.55)
    
    random_baseline = 33.33
    majority_baseline = 38.12
    plt.axhline(random_baseline, color='#e63946', linestyle=':', linewidth=1.5, label='Random 3-Class Baseline (33.3%)')
    plt.axhline(majority_baseline, color='#f4a261', linestyle='--', linewidth=1.5, label='Majority Class Baseline (38.1%)')

    plt.title('Random Forest Temporal Quality Prediction Performance Metrics', fontsize=13, fontweight='bold', pad=15)
    plt.ylabel('Score (%)', fontsize=11, labelpad=10)
    plt.ylim(0, 70)
    plt.grid(axis='y', alpha=0.7)
    plt.legend(loc='lower right', frameon=True)

    for bar, val in zip(bars, df['percentage']):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f'{val:.2f}%', 
                 ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1d3557')

    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '08_model_performance_metrics.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_class_distribution():
    path = os.path.join(EXPORT_DIR, 'spark_quality_prediction', 'confusion_matrix', 'part-00000-ae3b64a9-9ec2-4eb6-b5d4-f85c3720d315-c000.csv')
    df = pd.read_csv(path)
    
    actual_dist = df.groupby('actual_label')['count'].sum()
    pred_dist = df.groupby('predicted_label')['count'].sum()
    
    classes = ['Declining', 'Stable', 'Improving']
    actual_vals = [actual_dist.get(c, 0) for c in classes]
    pred_vals = [pred_dist.get(c, 0) for c in classes]
    
    x = np.arange(len(classes))
    width = 0.35

    plt.figure(figsize=(9, 5.5), dpi=300)
    b1 = plt.bar(x - width/2, actual_vals, width, label='Actual Test Ground Truth', color='#457b9d', edgecolor='#1d3557')
    b2 = plt.bar(x + width/2, pred_vals, width, label='Model Predictions', color='#e76f51', edgecolor='#9d0208')

    plt.title('Test Set Class Distribution: Ground Truth vs. Model Predictions', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Quality Trajectory Category', fontsize=11, labelpad=10)
    plt.ylabel('Number of Business-Year Pairs', fontsize=11, labelpad=10)
    plt.xticks(x, classes, fontsize=11, fontweight='semibold')
    plt.grid(axis='y', alpha=0.7)
    plt.legend(frameon=True)

    for bar in b1:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 100, f'{yval:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='semibold')
    for bar in b2:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 100, f'{yval:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='semibold')

    plt.ylim(0, max(max(actual_vals), max(pred_vals)) * 1.15)
    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '09_class_distribution_actual_vs_predicted.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_important_terms():
    terms_files = glob.glob(os.path.join(EXPORT_DIR, 'spark_business_quality', 'important_terms', '*.csv'))
    dfs = [pd.read_csv(f) for f in terms_files if os.path.getsize(f) > 0]
    df = pd.concat(dfs, ignore_index=True)
    df['rank'] = df['rank'].astype(int)
    top20 = df.sort_values('rank').head(20).sort_values('rank', ascending=False)

    plt.figure(figsize=(9.5, 6.5), dpi=300)
    colors = sns.color_palette("viridis", len(top20))
    bars = plt.barh(top20['term'], 21 - top20['rank'], color=colors, edgecolor='#333333', height=0.68)

    plt.title('Top 20 Most Frequent Meaningful Words in Customer Reviews (NLP CountVectorizer)', 
              fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Relative Importance Rank Score', fontsize=11, labelpad=10)
    plt.ylabel('Extracted Token / Term', fontsize=11, labelpad=10)
    plt.grid(axis='x', alpha=0.7)

    for bar, rank in zip(bars, top20['rank']):
        w = bar.get_width()
        plt.text(w + 0.2, bar.get_y() + bar.get_height()/2.0, f'Rank #{rank}', 
                 ha='left', va='center', fontsize=9, fontweight='semibold', color='#2b2d42')

    plt.xlim(0, 23)
    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '10_top_customer_terms.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_popularity_vs_quality():
    path = os.path.join(EXPORT_DIR, 'hive', 'popularity_vs_quality', '000000_0')
    df = pd.read_csv(path, sep='\t', header=None, 
                     names=['id', 'name', 'city', 'state', 'b_rating', 'b_rev_count', 'act_rev_count', 'avg_rev_rating'])
    
    plt.figure(figsize=(10.5, 6), dpi=300)
    
    scatter = plt.scatter(df['act_rev_count'], df['avg_rev_rating'], 
                          s=df['b_rating']*40, c=df['avg_rev_rating'], 
                          cmap='coolwarm', edgecolors='#1d3557', linewidth=1.5, alpha=0.85)
    
    cbar = plt.colorbar(scatter)
    cbar.set_label('Average Review Rating (Stars)', fontsize=10, labelpad=10)

    for _, row in df.head(8).iterrows():
        plt.annotate(f"{row['name']} ({row['state']})", 
                     (row['act_rev_count'], row['avg_rev_rating']),
                     xytext=(6, 4), textcoords='offset points', fontsize=8.5, fontweight='bold', color='#1d3557')

    plt.title('Popularity vs. Quality: Top Reviewed Yelp Businesses', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Review Volume (Total Reviews)', fontsize=11, labelpad=10)
    plt.ylabel('Empirical Mean Review Rating (Stars)', fontsize=11, labelpad=10)
    plt.grid(True, alpha=0.6)
    plt.ylim(2.2, 5.0)

    plt.tight_layout()
    out_path = os.path.join(VIZ_DIR, '11_popularity_vs_quality_scatter.png')
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == '__main__':
    print("Generating comprehensive visualization suite...")
    plot_rating_distribution()
    plot_state_business_distribution()
    plot_avg_rating_by_state()
    plot_state_review_vs_rating()
    plot_top_categories()
    plot_aspect_mentions()
    plot_confusion_matrix()
    plot_model_metrics()
    plot_class_distribution()
    plot_important_terms()
    plot_popularity_vs_quality()
    print("All 11 visualization charts generated successfully in visualizations/!")