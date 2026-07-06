#!/bin/sh
echo "Content-type: text/html; charset=utf-8"
echo ""

# Define base paths once for easy maintenance
BASE_DIR="/srv/www/images/blink"
VIDEO_DIR="/srv/www/videos/blink"
WEB_ROOT="/srv/www"

CURRENT_DIR="$BASE_DIR"
SHOW_RECENT=0

if [ -n "$QUERY_STRING" ]; then
    if [ "$QUERY_STRING" = "recent" ]; then
        SHOW_RECENT=1
    else
        DIR_ARG="${QUERY_STRING#dir=}"
        if [ -n "$DIR_ARG" ]; then
            CURRENT_DIR="$BASE_DIR$DIR_ARG"
        fi
    fi
fi

# Sanitize and resolve path to prevent directory traversal
# Using cd and pwd resolves symlinks, normalizes slashes, and removes trailing slashes
CURRENT_DIR=$(cd "$CURRENT_DIR" 2>/dev/null && pwd) || CURRENT_DIR="$BASE_DIR"
case "$CURRENT_DIR" in
    "$BASE_DIR"/*|"$BASE_DIR") ;;
    *) CURRENT_DIR="$BASE_DIR" ;;
esac

# Helper function to check for companion video
check_video() {
    _cv_vpath="${VIDEO_DIR}${1#$BASE_DIR}"
    [ -f "${_cv_vpath%.*}.mp4" ]
}

# Output Header and CSS using a Here-Doc (much cleaner than dozens of echo statements)
cat <<'EOF'
<html><head><title>Blink Gadget</title>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<style>
:root {
    --thumb-min-size: 150px;
    --thumb-max-height: 200px;
}

* { box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    margin: 10px;
    padding: 0;
    background: #f5f5f5;
}
h1 { font-size: 1.5em; margin: 10px 0; }
h2, h3 { font-size: 1.2em; margin: 10px 0; }
.dir {
    background: #f0f0f0;
    padding: 8px 12px;
    margin: 4px 6px 4px 0;
    display: inline-block;
    border-radius: 5px;
}
.dir a {
    text-decoration: none;
    color: #0066cc;
    font-size: 1em;
}
.dir a:hover { text-decoration: underline; }
.img-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--thumb-min-size), 1fr));
    gap: 10px;
    margin: 10px 0;
}
.img-item {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    cursor: pointer;
    position: relative;
}
.img-item img {
    width: 100%;
    height: auto;
    max-height: var(--thumb-max-height);
    object-fit: contain;
    border-radius: 4px;
}
.size-control {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #e8e8e8;
    padding: 8px 12px;
    border-radius: 5px;
    font-size: 0.9em;
    margin-bottom: 10px;
}
.size-control input[type="range"] {
    flex-grow: 1;
    cursor: pointer;
}
.img-item .video-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7em;
    pointer-events: none;
}
.breadcrumb {
    background: #e8e8e8;
    padding: 8px 10px;
    margin: 10px 0;
    border-radius: 5px;
    font-size: 0.9em;
    overflow-x: auto;
    white-space: nowrap;
}
.breadcrumb a {
    text-decoration: none;
    color: #0066cc;
}
.breadcrumb a:hover { text-decoration: underline; }
.nav-links {
    margin: 10px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.nav-links a {
    display: inline-block;
    padding: 8px 15px;
    background: #0066cc;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    font-size: 0.9em;
}
.nav-links a:hover { background: #0052a3; }
.nav-links a:active { transform: scale(0.95); }
p a {
    display: inline-block;
    padding: 8px 15px;
    background: #0066cc;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    font-size: 0.9em;
    margin: 5px 5px 5px 0;
}
p a:hover { background: #0052a3; }
p a:active { transform: scale(0.95); }
em { color: #888; font-style: italic; }

/* Touch-friendly improvements */
.dir a, .nav-links a, p a {
    touch-action: manipulation;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* Image viewer overlay */
.image-viewer {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    touch-action: none;
}
.image-viewer img {
    max-width: 80%; max-height: 80%;
    object-fit: contain;
    pointer-events: none;
}
.image-viewer video {
    max-width: 80%; max-height: 80%;
    object-fit: contain;
    background: #000;
}
.image-viewer .close {
    position: absolute;
    top: 20px; right: 20px;
    color: white;
    font-size: 30px;
    cursor: pointer;
    z-index: 10000;
    background: none;
    border: none;
    padding: 10px;
    min-height: 44px;
    min-width: 44px;
}
.image-viewer .nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(255,255,255,0.5);
    font-size: 40px;
    cursor: pointer;
    padding: 20px 10px;
    background: rgba(0,0,0,0.3);
    border: none;
    min-height: 44px;
    min-width: 44px;
    touch-action: manipulation;
}
.image-viewer .nav-btn:hover { color: white; background: rgba(0,0,0,0.5); }
.image-viewer .prev { left: 10px; }
.image-viewer .next { right: 10px; }
.image-viewer .counter {
    position: absolute;
    bottom: 20px;
    color: rgba(255,255,255,0.7);
    font-size: 14px;
}
.image-viewer .video-btn {
    position: absolute;
    bottom: 70px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255,255,255,0.2);
    color: white;
    border: 2px solid white;
    padding: 12px 24px;
    border-radius: 30px;
    font-size: 16px;
    cursor: pointer;
    min-height: 44px;
    min-width: 44px;
    touch-action: manipulation;
    z-index: 10000;
}
.image-viewer .video-btn:hover { background: rgba(255,255,255,0.3); }
.image-viewer .video-btn:active { transform: scale(0.95); }
.image-viewer .video-btn.hidden { display: none; }

/* Mobile-specific adjustments */
@media (max-width: 600px) {
    :root {
        --thumb-min-size: 120px;
        --thumb-max-height: 150px;
    }
    body { 
        margin: 5px; 
        font-size: 18px; /* Increase base font size for better readability */
    }
    h1 { font-size: 1.4em; }
    h2, h3 { font-size: 1.2em; }
    .img-grid { gap: 8px; }
    .dir {
        padding: 8px 12px;
        font-size: 1em;
        margin: 4px 6px 4px 0;
    }
    .breadcrumb { 
        font-size: 0.95em; 
        padding: 10px 12px; 
    }
    .nav-links a, p a {
        padding: 12px 15px;
        font-size: 1em;
        min-height: 44px;
    }
    .size-control {
        font-size: 1em;
        padding: 12px;
    }
    .size-control input[type="range"] {
        height: 30px; /* Larger touch target for the slider */
    }
    .image-viewer img, .image-viewer video {
        max-width: 95%;
        max-height: 75%;
    }
    .image-viewer .video-btn {
        bottom: 60px;
        padding: 12px 24px;
        font-size: 16px;
    }
}

@media (max-width: 400px) {
    :root {
        --thumb-min-size: 100px;
        --thumb-max-height: 120px;
    }
    body {
        font-size: 17px; /* Slightly adjusted for very small screens */
    }
    .img-grid { gap: 5px; }
    .img-item { padding: 5px; }
}
</style>
</head><body>
EOF

echo "<h1>📷 Blink Gadget</h1>"
echo "<div class='size-control'>"
echo "<span>🔍 Thumbnail Size:</span>"
echo "<input type='range' id='thumbSize' min='80' max='300' value='150' step='10'>"
echo "</div>"
echo "<div class='nav-links'>"

# Navigation links
PARENT_DIR="${CURRENT_DIR%/*}"
if [ "$CURRENT_DIR" != "$BASE_DIR" ] && [ "$CURRENT_DIR" != "$BASE_DIR/" ]; then
    PARENT_REL="${PARENT_DIR#$BASE_DIR}"
    echo "<a href='?dir=$PARENT_REL'>⬆ Up</a>"
fi
echo "<a href='?dir='>📁 Root</a>"
echo "<a href='?recent'>🕐 Recent</a>"
echo "</div>"

# Show 30 most recent view
if [ "$SHOW_RECENT" -eq 1 ]; then
    echo "<h2>30 Most Recent Events</h2>"
    echo "<div class='img-grid'>"

    ls -t "$BASE_DIR"/*/*/* 2>/dev/null | head -30 | while read img; do
        if [ -f "$img" ]; then
            url="${img#$WEB_ROOT}"
            has_video_flag=0
            if check_video "$img"; then has_video_flag=1; fi

            echo "<div class='img-item' data-video='$has_video_flag'>"
            echo "<a href='$url'><img src='$url' loading='lazy'></a>"
            if [ "$has_video_flag" -eq 1 ]; then
                echo "<span class='video-badge'>🎬</span>"
            fi
            echo "</div>"
        fi
    done

    echo "</div>"
    echo "<p><a href='?dir='>📁 Root</a> <a href='?recent'>🕐 Recent</a></p>"
else
    # Breadcrumb navigation
    echo "<div class='breadcrumb'>📂 <a href='?dir='>root</a>"

    CURRENT_DIR_NO_PREFIX="${CURRENT_DIR#$BASE_DIR}"
    if [ -n "$CURRENT_DIR_NO_PREFIX" ] && [ "$CURRENT_DIR_NO_PREFIX" != "/" ]; then
        CURRENT_DIR_NO_PREFIX="${CURRENT_DIR_NO_PREFIX#/}"

        FULL_PATH=""
        OLD_IFS="$IFS"
        IFS='/'
        for part in $CURRENT_DIR_NO_PREFIX; do
            if [ -n "$part" ]; then
                if [ -z "$FULL_PATH" ]; then
                    FULL_PATH="/$part"
                else
                    FULL_PATH="$FULL_PATH/$part"
                fi
                echo " › <a href='?dir=$FULL_PATH'>$part</a>"
            fi
        done
        IFS="$OLD_IFS"
    fi
    echo "</div>"

    # Show subdirectories sorted by most recent first
    echo "<h3>📁 Subdirectories</h3>"
    DIR_LIST=$(ls -dt "$CURRENT_DIR"/*/ 2>/dev/null)

    if [ -z "$DIR_LIST" ]; then
        echo "<p><em>No subdirectories</em></p>"
    else
        echo "$DIR_LIST" | while read dir; do
            if [ -d "$dir" ]; then
                dirname=$(basename "$dir")
                rel_path="${dir#$BASE_DIR}"
                rel_path="${rel_path%/}"
                echo "<div class='dir'><a href='?dir=$rel_path'>📁 $dirname/</a></div>"
            fi
        done
    fi
    echo "<br>"

    # Show images in current directory (most recent first)
    echo "<h3>🖼️ Images in $(basename "$CURRENT_DIR")</h3>"
    echo "<div class='img-grid'>"

    IMAGE_LIST=$(ls -t "$CURRENT_DIR"/*.jpg "$CURRENT_DIR"/*.jpeg "$CURRENT_DIR"/*.png "$CURRENT_DIR"/*.gif 2>/dev/null | head -20)

    if [ -z "$IMAGE_LIST" ]; then
        echo "<p><em>No images in this directory</em></p>"
    else
        echo "$IMAGE_LIST" | while read img; do
            if [ -f "$img" ]; then
                url="${img#$WEB_ROOT}"
                has_video_flag=0
                if check_video "$img"; then has_video_flag=1; fi

                echo "<div class='img-item' data-video='$has_video_flag'>"
                echo "<a href='$url'><img src='$url' loading='lazy'></a>"
                if [ "$has_video_flag" -eq 1 ]; then
                    echo "<span class='video-badge'>🎬</span>"
                fi
                echo "</div>"
            fi
        done
    fi
    echo "</div>"

    # Navigation footer
    echo "<p>"
    PARENT_DIR="${CURRENT_DIR%/*}"
    if [ "$CURRENT_DIR" != "$BASE_DIR" ] && [ "$CURRENT_DIR" != "$BASE_DIR/" ]; then
        PARENT_REL="${PARENT_DIR#$BASE_DIR}"
        echo "<a href='?dir=$PARENT_REL'>⬆ Up</a> "
    fi
    echo "<a href='?dir='>📁 Root</a>"
    echo " <a href='?recent'>🕐 Recent</a>"
    echo "</p>"
fi

# Output JavaScript and Footer using a Here-Doc
cat <<'EOF'
<script>
(function() {
    // Thumbnail size control logic
    var sizeSlider = document.getElementById('thumbSize');
    if (sizeSlider) {
        var savedSize = localStorage.getItem('blinkThumbSize');

        function applySize(size) {
            document.documentElement.style.setProperty('--thumb-min-size', size + 'px');
            document.documentElement.style.setProperty('--thumb-max-height', (size * 1.33) + 'px');
            sizeSlider.value = size;
        }

        if (savedSize) {
            applySize(savedSize);
        } else {
            // Set slider to current computed value without overriding CSS variables
            var computedSize = window.getComputedStyle(document.documentElement).getPropertyValue('--thumb-min-size').replace('px', '').trim();
            sizeSlider.value = computedSize || 150;
        }

        sizeSlider.addEventListener('input', function() {
            applySize(this.value);
            localStorage.setItem('blinkThumbSize', this.value);
        });
    }

    var currentIndex = 0;
    var imageList = [];
    var videoList = [];
    var startX = 0;
    var startY = 0;
    var isSwiping = false;
    var isRecentView = window.location.search.indexOf('recent') !== -1;
    var isVideoMode = false;

    document.querySelectorAll('.img-item').forEach(function(item, index) {
        var link = item.querySelector('a');
        if (link) {
            imageList.push(link.getAttribute('href'));
            var hasVideo = item.getAttribute('data-video') === '1';
            videoList.push(hasVideo);
        }
    });

    var urlParams = new URLSearchParams(window.location.search);
    var viewImg = urlParams.get('view');
    if (viewImg) {
        var index = imageList.indexOf(viewImg);
        if (index !== -1) {
            currentIndex = index;
            showViewer();
        }
    }

    document.querySelectorAll('.img-item a').forEach(function(link, index) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            currentIndex = index;
            isVideoMode = false;
            var baseUrl = window.location.pathname;
            var params = isRecentView ? 'recent' : 'dir=' + (urlParams.get('dir') || '');
            var newUrl = baseUrl + '?' + params + '&view=' + encodeURIComponent(this.getAttribute('href'));
            window.history.pushState({}, '', newUrl);
            showViewer();
        });
    });

    function getVideoPath(imagePath) {
        // imagePath comes as /images/blink/26-07/26-07-05/file.jpg
        // Convert to /videos/blink/26-07/26-07-05/file.mp4
        var videoPath = imagePath.replace('/images/blink/', '/videos/blink/');
        videoPath = videoPath.replace(/\.[^.]+$/, '.mp4');
        return videoPath;
    }

    function showViewer() {
        if (imageList.length === 0) return;

        var viewer = document.createElement('div');
        viewer.className = 'image-viewer';
        viewer.id = 'imageViewer';

        var close = document.createElement('button');
        close.className = 'close';
        close.innerHTML = '✕';
        close.addEventListener('click', hideViewer);
        viewer.appendChild(close);

        var prev = document.createElement('button');
        prev.className = 'nav-btn prev';
        prev.innerHTML = '‹';
        prev.addEventListener('click', function(e) {
            e.stopPropagation();
            if (currentIndex > 0) {
                navigate(-1);
            }
        });
        viewer.appendChild(prev);

        var next = document.createElement('button');
        next.className = 'nav-btn next';
        next.innerHTML = '›';
        next.addEventListener('click', function(e) {
            e.stopPropagation();
            if (currentIndex < imageList.length - 1) {
                navigate(1);
            }
        });
        viewer.appendChild(next);

        // Create container for both image and video
        var mediaContainer = document.createElement('div');
        mediaContainer.style.position = 'relative';
        mediaContainer.style.width = '100%';
        mediaContainer.style.height = '100%';
        mediaContainer.style.display = 'flex';
        mediaContainer.style.justifyContent = 'center';
        mediaContainer.style.alignItems = 'center';

        var img = document.createElement('img');
        img.id = 'viewerImage';
        img.style.maxWidth = '80%';
        img.style.maxHeight = '80%';
        img.style.objectFit = 'contain';
        mediaContainer.appendChild(img);

        var video = document.createElement('video');
        video.id = 'viewerVideo';
        video.style.maxWidth = '80%';
        video.style.maxHeight = '80%';
        video.style.objectFit = 'contain';
        video.style.background = '#000';
        video.style.display = 'none';
        video.controls = true;
        mediaContainer.appendChild(video);

        viewer.appendChild(mediaContainer);

        var counter = document.createElement('div');
        counter.className = 'counter';
        counter.id = 'viewerCounter';
        viewer.appendChild(counter);

        // Video toggle button
        var videoBtn = document.createElement('button');
        videoBtn.className = 'video-btn';
        videoBtn.textContent = '🎬 Play Video';
        videoBtn.id = 'videoBtn';
        videoBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleVideo();
        });
        viewer.appendChild(videoBtn);

        document.body.appendChild(viewer);

        viewer.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isSwiping = false;
        }, { passive: true });

        viewer.addEventListener('touchmove', function(e) {
            if (e.touches.length === 1) {
                var deltaX = e.touches[0].clientX - startX;
                var deltaY = e.touches[0].clientY - startY;
                if (Math.abs(deltaX) > 10 && Math.abs(deltaX) > Math.abs(deltaY)) {
                    isSwiping = true;
                    e.preventDefault();
                }
            }
        }, { passive: false });

        viewer.addEventListener('touchend', function(e) {
            if (isSwiping) {
                var endX = e.changedTouches[0].clientX;
                var deltaX = endX - startX;
                if (deltaX < -50 && currentIndex < imageList.length - 1) {
                    navigate(1);
                } else if (deltaX > 50 && currentIndex > 0) {
                    navigate(-1);
                }
            }
            isSwiping = false;
        }, { passive: true });

        document.addEventListener('keydown', keyHandler);
        updateImage();
    }

    function updateImage() {
        if (imageList.length === 0) return;

        var img = document.getElementById('viewerImage');
        var video = document.getElementById('viewerVideo');
        var counter = document.getElementById('viewerCounter');
        var prevBtn = document.querySelector('.nav-btn.prev');
        var nextBtn = document.querySelector('.nav-btn.next');
        var videoBtn = document.getElementById('videoBtn');

        var currentImage = imageList[currentIndex];
        var hasVideo = videoList[currentIndex];

        if (img) {
            img.src = currentImage;
            img.style.display = isVideoMode ? 'none' : 'block';
        }

        if (video) {
            if (hasVideo && isVideoMode) {
                var videoPath = getVideoPath(currentImage);
                video.src = videoPath;
                video.style.display = 'block';
                video.load();
                video.play().catch(function(e) {
                    console.log('Auto-play prevented:', e);
                });
            } else {
                video.style.display = 'none';
                video.pause();
                video.src = '';
            }
        }

        if (videoBtn) {
            if (hasVideo) {
                videoBtn.style.display = 'block';
                videoBtn.textContent = isVideoMode ? '📷 Show Image' : '🎬 Play Video';
            } else {
                videoBtn.style.display = 'none';
            }
        }

        if (counter) {
            counter.textContent = (currentIndex + 1) + ' / ' + imageList.length;
        }

        if (prevBtn) {
            if (currentIndex <= 0) {
                prevBtn.style.opacity = '0.2';
                prevBtn.style.pointerEvents = 'none';
            } else {
                prevBtn.style.opacity = '1';
                prevBtn.style.pointerEvents = 'auto';
            }
        }

        if (nextBtn) {
            if (currentIndex >= imageList.length - 1) {
                nextBtn.style.opacity = '0.2';
                nextBtn.style.pointerEvents = 'none';
            } else {
                nextBtn.style.opacity = '1';
                nextBtn.style.pointerEvents = 'auto';
            }
        }

        var urlParams = new URLSearchParams(window.location.search);
        var baseUrl = window.location.pathname;
        var params = isRecentView ? 'recent' : 'dir=' + (urlParams.get('dir') || '');
        var newUrl = baseUrl + '?' + params + '&view=' + encodeURIComponent(currentImage);
        if (isVideoMode) {
            newUrl += '&video=1';
        }
        window.history.replaceState({}, '', newUrl);
    }

    function toggleVideo() {
        isVideoMode = !isVideoMode;
        updateImage();
    }

    function navigate(direction) {
        var newIndex = currentIndex + direction;
        if (newIndex < 0 || newIndex >= imageList.length) {
            return;
        }
        currentIndex = newIndex;
        isVideoMode = false;
        updateImage();
    }

    function hideViewer() {
        var viewer = document.getElementById('imageViewer');
        if (viewer) {
            var video = document.getElementById('viewerVideo');
            if (video) {
                video.pause();
                video.src = '';
            }
            viewer.remove();
        }
        document.removeEventListener('keydown', keyHandler);
        var urlParams = new URLSearchParams(window.location.search);
        var baseUrl = window.location.pathname;
        var params = isRecentView ? 'recent' : 'dir=' + (urlParams.get('dir') || '');
        window.history.replaceState({}, '', baseUrl + '?' + params);
    }

    function keyHandler(e) {
        if (e.key === 'Escape') {
            hideViewer();
        } else if (e.key === 'ArrowLeft') {
            if (currentIndex > 0) {
                navigate(-1);
                e.preventDefault();
            }
        } else if (e.key === 'ArrowRight') {
            if (currentIndex < imageList.length - 1) {
                navigate(1);
                e.preventDefault();
            }
        } else if (e.key === 'v' || e.key === 'V') {
            toggleVideo();
            e.preventDefault();
        } else if (e.key === ' ' && isVideoMode) {
            var video = document.getElementById('viewerVideo');
            if (video) {
                e.preventDefault();
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            }
        }
    }

    window.addEventListener('popstate', function() {
        var viewer = document.getElementById('imageViewer');
        if (viewer) {
            hideViewer();
        }
    });

    // Check for video mode in URL
    var urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('video') === '1') {
        isVideoMode = true;
        // We need to wait for viewer to be created
        setTimeout(function() {
            var videoBtn = document.getElementById('videoBtn');
            if (videoBtn) {
                toggleVideo();
            }
        }, 100);
    }
})();
</script>
</body></html>
EOF
