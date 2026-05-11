# Sayid2
import streamlit as st
from apify_client import ApifyClient
from openai import OpenAI

# App Title & Configuration
st.set_page_config(page_title="Sayid2 AI", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Sayid2: VIP Search AI")
st.markdown("---")

# Sidebar for Image Upload (optional feature you requested)
st.sidebar.header("Upload Image")
uploaded_file = st.sidebar.file_uploader("Add a photo of the person:", type=['jpg', 'png', 'jpeg'])
if uploaded_file:
    st.sidebar.image(uploaded_file, caption="Target Person")

# Main Input
target_name = st.text_input("Enter the Name of the Person:", placeholder="e.g. John Doe")

if st.button("Start AI Search"):
    if not target_name:
        st.warning("Please enter a name first.")
    else:
        with st.spinner(f"Sayid2 is scanning social media for {target_name}..."):
            try:
                # 1. Connect to Apify (Social Media Discovery)
                apify_client = ApifyClient(st.secrets["APIFY_TOKEN"])
                
                # Running the search actor (Public Data Search)
                run_input = {
                    "profileNames": [target_name],
                    "socials": ["instagram", "tiktok"]
                }
                run = apify_client.actor("tri_angle/social-media-finder").call(run_input=run_input)
                results = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())

                if results:
                    # 2. AI Summarization (OpenAI)
                    ai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                    
                    prompt = f"I found the following raw data for {target_name}: {results}. " \
                             f"Please provide a clean summary in English. Mention their profession if found " \
                             f"and list their Instagram/TikTok links clearly."

                    response = ai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "You are Sayid2, a professional investigative AI."},
                                  {"role": "user", "content": prompt}]
                    )
                    
                    ai_summary = response.choices[0].message.content

                    # 3. Display Results
                    st.success("Search Complete!")
                    st.subheader("🤖 AI Analysis Result:")
                    st.markdown(ai_summary)
                    
                    # Highlight Links
                    st.divider()
                    st.write("🔗 **Direct Social Links:**")
                    for item in results:
                        link = item.get('url', 'No link found')
                        st.write(f"- {link}")

                else:
                    st.error("No public information found for this name.")

            except Exception as e:
                st.error(f"An error occurred. Make sure your API Keys are set in Streamlit Secrets.")

