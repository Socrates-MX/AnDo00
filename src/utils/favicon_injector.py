import base64
import streamlit as st

def inject_favicons(path_16, path_32, path_apple):
    with open(path_16, "rb") as f:
        b16 = base64.b64encode(f.read()).decode()
    with open(path_32, "rb") as f:
        b32 = base64.b64encode(f.read()).decode()
    with open(path_apple, "rb") as f:
        b180 = base64.b64encode(f.read()).decode()
        
    favicon_html = f"""
    <script>
        (function() {{
            var link16 = window.parent.document.createElement('link');
            link16.rel = 'icon';
            link16.type = 'image/png';
            link16.sizes = '16x16';
            link16.href = 'data:image/png;base64,{b16}';
            window.parent.document.getElementsByTagName('head')[0].appendChild(link16);

            var link32 = window.parent.document.createElement('link');
            link32.rel = 'icon';
            link32.type = 'image/png';
            link32.sizes = '32x32';
            link32.href = 'data:image/png;base64,{b32}';
            window.parent.document.getElementsByTagName('head')[0].appendChild(link32);

            var appleLink = window.parent.document.createElement('link');
            appleLink.rel = 'apple-touch-icon';
            appleLink.sizes = '180x180';
            appleLink.href = 'data:image/png;base64,{b180}';
            window.parent.document.getElementsByTagName('head')[0].appendChild(appleLink);
        }})();
    </script>
    """
    st.markdown(favicon_html, unsafe_allow_html=True)
