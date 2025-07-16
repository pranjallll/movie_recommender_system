mkdir -p ~/.streamlit/

echo "\
[server]\n\
port =$PORT\N\
enableCORS = true\n\
\n\
" > ~/.streamlit/config.toml