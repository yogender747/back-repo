import os

# Determine the project root (assumes songRecommender is in project-root)
project_root = os.path.join(os.path.dirname(__file__), "..")

# Relative paths for new.html and new.txt
new_html_path = os.path.join(project_root, "new.html")
new_txt_path = os.path.join(project_root, "new.txt")

with open(new_txt_path, "r") as f2:
    p = f2.read().strip()

html_content = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MoodSync Playlist</title>
    <style>
      /* General Styles */
      body {{
        font-family: Arial, sans-serif;
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        overflow: hidden;
      }}
      /* Background Video */
      .video-background {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: -1;
      }}
      /* Container to center the iframe */
      .iframe-container {{
        position: relative;
        width: 75%;
        height: 75%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.6);
      }}
      iframe {{
        width: 100%;
        height: 100%;
        border-radius: 12px;
        border: none;
      }}
    </style>
  </head>
  <body>
    <!-- Background Video -->
    <video class="video-background" autoplay loop muted>
      <source src="/videos/background.mp4" type="video/mp4">
      Your browser does not support the video tag.
    </video>

    <div class="iframe-container">
      <iframe src="https://open.spotify.com/embed/playlist/{p}?utm_source=generator" 
        allow="autoplay; clipboard-write; encrypted-media; picture-in-picture" loading="lazy">
      </iframe>
    </div>
  </body>
</html>'''

with open(new_html_path, "w") as fp:
    fp.write(html_content)

# Instead of attempting to open the HTML file (which won’t work in a headless environment),
# simply print its location.
print("New HTML file generated at:", new_html_path)
