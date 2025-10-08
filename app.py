
import streamlit as st 
from story_generator import generate_story_from_images, narrate_story
from PIL import Image
# building interfact 

st.title("AI Story Generator from Image. ")
st.markdown("Upload 1-10 images, choose an style and let AI write and narrate a story for you.")

# building control 

with st.sidebar: 
    st.header("Controls")

    # side option to upload images 

    uploaded_files = st.file_uploader(
        "Upload your images...", 
        type = ['png', 'jpeg', 'jpg'], 
        accept_multiple_files= True 
    )


    # side option to select the theme of the story 

    story_style = st.selectbox(
        "Choose a story style.", 
        ('Comedy', 'Thriller', 'Fairy Tale', 'Sci-Fi', 'Mystery', 'Adventure', 'Morale') # options
    )

    # generation button 

    generate_button = st.button("Generate Story and Narration", type= 'primary')

    # main logic 
    # when the generate button is presseed, the image sent to model and based on the image model generates the story

if generate_button: 
    if not uploaded_files: 
        st.warning("Please upload atleast one image")

    elif len(uploaded_files) > 10: 
        st.warning("Not more than 10 images allowed. Please upload maximum of 10 images.")

    else: 
        with st.spinner("The AI is writing is your story... This may take few moments."):
            try: 
                pil_images = [Image.open(uploaded_file) for uploaded_file in uploaded_files]
                st.subheader("Your visuals Inspiration.") 
                image_columns = st.columns(len(pil_images))

                for i, image in enumerate(pil_images): 
                    with image_columns[i]: 
                        st.image(image, use_container_width= True) 

                generate_story = generate_story_from_images(pil_images, story_style)

                if "Error" in generate_story or "failed" in generate_story or "API key" in generate_story: 
                    st.error(generate_story)
                
                else: 
                    st.subheader(f"Your {story_style} story: ")
                    st.success(generate_story)

                st.subheader("Listen to your story here: ")
                audio_file= narrate_story(generate_story)
                if audio_file: 
                    st.audio(audio_file, format= 'audio/mp3') 

            except Exception as e: 
                st.error(f"An application error has occured. {e}")

