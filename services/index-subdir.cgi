#!/bin/sh
echo "Content-type: text/html; charset=utf-8"
echo ""

echo "<html><head><title>Blink Gadget</title>"
echo "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
echo "<style>
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
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
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
}
.img-item img {
    width: 100%;
    height: auto;
    max-height: 200px;
    object-fit: contain;
    border-radius: 4px;
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
.nav-links a:hover {
    background: #0052a3;
}
.nav-links a:active {
    transform: scale(0.95);
}
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
p a:hover {
    background: #0052a3;
}
p a:active {
    transform: scale(0.95);
}
em {
    color: #888;
    font-style: italic;
}

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
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    touch-action: none;
}
.image-viewer img {
    max-width: 95%;
    max-height: 95%;
    object-fit: contain;
    pointer-events: none;
}
.image-viewer .close {
    position: absolute;
    top: 20px;
    right: 20px;
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
.image-viewer .nav-btn:hover {
    color: white;
    background: rgba(0,0,0,0.5);
}
.image-viewer .prev { left: 10px; }
.image-viewer .next { right: 10px; }
.image-viewer .counter {
    position: absolute;
    bottom: 20px;
    color: rgba(255,255,255,0.7);
    font-size: 14px;
}

/* Mobile-specific adjustments */
@media (max-width: 600px) {
    body { margin: 5px; }
    h1 { font-size: 1.2em; }
    .img-grid {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 8px;
    }
    .img-item img { max-height: 150px; }
    .dir {
        padding: 6px 10px;
        font-size: 0.9em;
        margin: 3px 4px 3px 0;
    }
    .breadcrumb {
        font-size: 0.8em;
        padding: 6px 8px;
    }
    .nav-links a, p a {
        padding: 10px 12px;
        font-size: 0.85em;
        min-height: 44px;
    }
}

@media (max-width: 400px) {
    .img-grid {
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: 5px;
    }
    .img-item { padding: 5px; }
    .img-item img { max-height: 120px; }
}
</style>"
echo "</head><body>"

# Get the current directory from query string
CURRENT_DIR="/srv/www/blink"
SHOW_RECENT=0

if [ -n "$QUERY_STRING" ]; then
    # Check if we want to show recent view
    if [ "$QUERY_STRING" = "recent" ]; then
        SHOW_RECENT=1
    else
        DIR_ARG="${QUERY_STRING#dir=}"
        if [ -n "$DIR_ARG" ]; then
            CURRENT_DIR="/srv/www/blink$DIR_ARG"
        fi
    fi
fi

# Sanitize - prevent directory traversal
case "$CURRENT_DIR" in
    /srv/www/blink/*)
        CURRENT_DIR=$(echo "$CURRENT_DIR" | sed 's|//*|/|g')
        ;;
    *)
        CURRENT_DIR="/srv/www/blink"
        ;;
esac

if [ ! -d "$CURRENT_DIR" ]; then
    CURRENT_DIR="/srv/www/blink"
fi

echo "<h1>📷 Blink Gadget</h1>"

# Navigation links
echo "<div class='nav-links'>"
# Get parent directory for "Up" button
PARENT_DIR="${CURRENT_DIR%/*}"
if [ "$CURRENT_DIR" != "/srv/www/blink" ] && [ "$CURRENT_DIR" != "/srv/www/blink/" ]; then
    PARENT_REL="${PARENT_DIR#/srv/www/blink}"
    echo "<a href='?dir=$PARENT_REL'>⬆ Up</a>"
fi
echo "<a href='?dir='>📁 Root</a>"
echo "<a href='?recent'>🕐 Recent</a>"
echo "</div>"

# Show 30 most recent view
if [ $SHOW_RECENT -eq 1 ]; then
    echo "<h2>30 Most Recent Events</h2>"
    echo "<div class='img-grid'>"

    ls -t /srv/www/blink/*/*/* 2>/dev/null | head -30 | while read img; do
        if [ -f "$img" ]; then
            url="${img#/srv/www}"
            echo "<div class='img-item'>"
            echo "<a href='$url'><img src='$url' loading='lazy'></a>"
            echo "</div>"
        fi
    done

    echo "</div>"
    echo "<p><a href='?dir='>📁 Root</a> <a href='?recent'>🕐 Recent</a></p>"
else
    # Breadcrumb navigation
    echo "<div class='breadcrumb'>📂 <a href='?dir='>root</a>"

    # Build breadcrumb by splitting path manually
    CURRENT_DIR_NO_PREFIX="${CURRENT_DIR#/srv/www/blink}"
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
                rel_path="${dir#/srv/www/blink}"
                rel_path="${rel_path%/}"
                echo "<div class='dir'><a href='?dir=$rel_path'>📁 $dirname/</a></div>"
            fi
        done
    fi
    echo "<br>"

    # Show images in current directory (most recent first)
    echo "<h3>🖼️ Images in $(basename "$CURRENT_DIR")</h3>"
    echo "<div class='img-grid'>"

    # Check if any images exist first
    IMAGE_LIST=$(ls -t "$CURRENT_DIR"/*.jpg "$CURRENT_DIR"/*.jpeg "$CURRENT_DIR"/*.png "$CURRENT_DIR"/*.gif 2>/dev/null | head -20)

    if [ -z "$IMAGE_LIST" ]; then
        echo "<p><em>No images in this directory</em></p>"
    else
        echo "$IMAGE_LIST" | while read img; do
            if [ -f "$img" ]; then
                url="${img#/srv/www}"
                echo "<div class='img-item'>"
                echo "<a href='$url'><img src='$url' loading='lazy'></a>"
                echo "</div>"
            fi
        done
    fi

    echo "</div>"

    # Navigation footer
    echo "<p>"
    # Get parent directory for "Up" button
    PARENT_DIR="${CURRENT_DIR%/*}"
    if [ "$CURRENT_DIR" != "/srv/www/blink" ] && [ "$CURRENT_DIR" != "/srv/www/blink/" ]; then
        PARENT_REL="${PARENT_DIR#/srv/www/blink}"
        echo "<a href='?dir=$PARENT_REL'>⬆ Up</a> "
    fi
    echo "<a href='?dir='>📁 Root</a>"
    echo " <a href='?recent'>🕐 Recent</a>"
    echo "</p>"
fi

# Single JavaScript for both views
echo "<script>
(function() {
    var currentIndex = 0;
    var imageList = [];
    var startX = 0;
    var startY = 0;
    var isSwiping = false;
    var isRecentView = window.location.search.indexOf('recent') !== -1;

    document.querySelectorAll('.img-item a').forEach(function(link) {
        imageList.push(link.getAttribute('href'));
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
            var baseUrl = window.location.pathname;
            var params = isRecentView ? 'recent' : 'dir=' + (urlParams.get('dir') || '');
            var newUrl = baseUrl + '?' + params + '&view=' + encodeURIComponent(this.getAttribute('href'));
            window.history.pushState({}, '', newUrl);
            showViewer();
        });
    });

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

        var img = document.createElement('img');
        img.id = 'viewerImage';
        viewer.appendChild(img);

        var counter = document.createElement('div');
        counter.className = 'counter';
        counter.id = 'viewerCounter';
        viewer.appendChild(counter);

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
        var counter = document.getElementById('viewerCounter');
        var prevBtn = document.querySelector('.nav-btn.prev');
        var nextBtn = document.querySelector('.nav-btn.next');

        if (img) {
            img.src = imageList[currentIndex];
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
        var newUrl = baseUrl + '?' + params + '&view=' + encodeURIComponent(imageList[currentIndex]);
        window.history.replaceState({}, '', newUrl);
    }

    function navigate(direction) {
        var newIndex = currentIndex + direction;
        if (newIndex < 0 || newIndex >= imageList.length) {
            return;
        }
        currentIndex = newIndex;
        updateImage();
    }

    function hideViewer() {
        var viewer = document.getElementById('imageViewer');
        if (viewer) {
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
        }
    }

    window.addEventListener('popstate', function() {
        var viewer = document.getElementById('imageViewer');
        if (viewer) {
            hideViewer();
        }
    });
})();
</script>"

echo "</body></html>"
