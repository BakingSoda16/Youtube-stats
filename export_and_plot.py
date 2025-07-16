import json
import matplotlib.pyplot as plt
from youtube_video_stats import main as fetch_video_data

def export_to_json(videos, filename="video_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=4, ensure_ascii=False)
    print(f"✅ Data exported to {filename}")

def plot_views(videos):
    if not videos:
        print("No data to plot.")
        return

    # Sort videos by views descending
    videos_sorted = sorted(videos, key=lambda x: x["views"], reverse=True)
    
    # Take top 10 for readability
    top_videos = videos_sorted[:10]
    titles = [v["title"][:30] + "..." if len(v["title"]) > 30 else v["title"] for v in top_videos]
    views = [v["views"] for v in top_videos]

    plt.figure(figsize=(12, 6))
    plt.barh(titles[::-1], views[::-1], color='skyblue')
    plt.xlabel("Views")
    plt.title("Top 10 Most Viewed Videos")
    plt.tight_layout()
    plt.savefig("top_10_videos.png")
    plt.show()

if __name__ == "__main__":
    videos = fetch_video_data()
    if videos:
        export_to_json(videos)
        plot_views(videos)
