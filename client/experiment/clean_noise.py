import os

def clean_text_file(input_file):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean up line breaks
    # Replace multiple newlines with single newline
    cleaned_content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
    
    # Generate output filename
    output_file = input_file.rsplit('.', 1)[0] + '_cleaned.txt'
    
    # Write the cleaned content to new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Cleaned file saved as: {output_file}")

if __name__ == "__main__":
    input_file = "noise.txt"
    clean_text_file(input_file) 