import docx 
import openai 
import json
import replicate
import os

openai.api_key = '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'

def gpt3prompt(text,key):
    prompts = {
        1 : "Identify key characters from the following script and write a short description of them:",
        2 : "Based on the input given just return a string python dictionary without any escape sequences, with key as characetr's name and value as description",
        3 : "Based on the characters descriptioned mentioned below, generate a physical description of each of the characters, provide details about their facial structure, hair color, shape of eyes, expresion of the face, color of eyes, body structure and other essential features. Make each character look unique from each other"
    }

    prompt = prompts.get(key) + text 

    gpt3_response = openai.Completion.create(
        model="text-davinci-003",
        prompt= prompt,
        max_tokens=2000,
        temperature=0
    )

    output_txt = gpt3_response.get('choices')[0].get('text')
    return output_txt


def generate_image(prompt):
    model = replicate.models.get("prompthero/openjourney")
    version = model.versions.get("9936c2001faa2194a261c01381f90e65261879985476014a0a37a334593a05eb")

    # https://replicate.com/prompthero/openjourney/versions/9936c2001faa2194a261c01381f90e65261879985476014a0a37a334593a05eb#input
    inputs = {
        # Input prompt
        'prompt': prompt,

        # Width of output image. Maximum size is 1024x768 or 768x1024 because
        # of memory limits
        'width': 512,

        # Height of output image. Maximum size is 1024x768 or 768x1024 because
        # of memory limits
        'height': 512,

        # Number of images to output
        'num_outputs': 4,

        # Number of denoising steps
        # Range: 1 to 500
        'num_inference_steps': 50,

        # Scale for classifier-free guidance
        # Range: 1 to 20
        'guidance_scale': 6,

        # Random seed. Leave blank to randomize the seed
        # 'seed': ...,
    }

    # https://replicate.com/prompthero/openjourney/versions/9936c2001faa2194a261c01381f90e65261879985476014a0a37a334593a05eb#output-schema
    output = version.predict(**inputs)
    return output

def add_image_to_markdown(image_url, markdown_file_path):
    """
    Add an image with the given URL to the markdown file at the given file path.
    """
    # Extract the image filename from the URL
    image_filename = os.path.basename(image_url)
    
    # Format the markdown syntax for the image
    image_markdown = f"![{image_filename}]({image_url})"
    
    # Open the markdown file and append the image markdown to the end of the file
    with open(markdown_file_path, "a") as markdown_file:
        markdown_file.write(image_markdown)
        markdown_file.write("\n")

image_presets = [
    " Perfect composition, hyperrealistic, super detailed, 8k, high quality, trending art, trending on artstation, sharp focus, studio photo, intricate details, highly detailed, by greg rutkowski",
    " Detailed face, by makoto shinkai, stanley artgerm lau, wlop, rossdraws, concept art, digital painting, looking into camera",
    " New Realism, Art by Vincent Di Fate, super detailed, 8k, high quality",
    " Photo realism, Art by James Gurney, hyperrealistic, 8k, high quality",
    " Detailed, concept art, digital painting, anime, manga, animecore, high quality",
]

filename = "/Users/sanket/Downloads/Ep 1 - A windfall from thin air.docx"
markdown_file = "/Users/sanket/code/nlp/the_rich_and_reckless_husband.md"

input_file = docx.Document(filename)

episode = ""
for para in input_file.paragraphs:
    episode += para.text 

characters = {}

i = 0
j = 8000
while i < len(episode):
    para = episode[i:j]
    response = gpt3prompt(para,1)
    response2 = gpt3prompt(response, 2)
    temp = response2.split("Answer:",1)
    temp_dict = json.loads(temp[-1])
    for k,v in temp_dict.items():
        if k not in characters:
            characters[k] = v
    i += 8000
    j += 8000


response = gpt3prompt(str(characters), 3)
response2 = gpt3prompt(response, 2)
print(response2)
temp_dict = response2.split("{",1)
temp_dict = "{" + temp_dict[-1]
characters_description = json.loads(temp_dict)


for character, description in characters_description.items():
    for preset in image_presets:
        prompt = "mdjrny-v4 style" +description + preset
        output = generate_image(prompt)
        for url in output:
            add_image_to_markdown(url,markdown_file)
