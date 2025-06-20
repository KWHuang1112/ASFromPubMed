import os
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
class Txt2ShortHz:
    def __init__(self, filename, pubmed_id):
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read().replace('\n', ' ')
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            upper = sentence.upper().strip()

            if 'HZ' in upper:
                hz_positions = self.get_hz_positions(upper)

                for pos in hz_positions:
                    start = max(0, pos - 20)
                    end = min(len(upper), pos + 2)
                    snippet = upper[start:end]
                    digits = self.extract_numbers(snippet)
                    print(f"{pubmed_id}\t{sentence.strip()}\t{snippet}\t{digits}")

    def get_hz_positions(self, s):
        positions = []
        index = s.find("HZ")
        while index != -1:
            positions.append(index + 2)
            index = s.find("HZ", index + 2)
        return positions

    def extract_numbers(self, snippet):
        snippet = re.sub(r'\bAND\b', ' AND ', snippet)
        snippet = re.sub(r'\bTO\b', ' TO ', snippet)
        snippet = re.sub(r'[,()\–∼-]', ' ', snippet)
        tokens = snippet.split()
        result = []

        for token in tokens:
            try:
                result.append(str(float(token)))
            except ValueError:
                continue

        return ', '.join(result)


class ManyFileTxt2FormatMod3:
    def __init__(self, root_dir):
        if not os.path.isdir(root_dir):
            print("Invalid directory.")
            return

        for sub_dir_name in os.listdir(root_dir):
            sub_dir_path = os.path.join(root_dir, sub_dir_name)
            if not os.path.isdir(sub_dir_path):
                continue

            for file_name in os.listdir(sub_dir_path):
                if file_name.endswith('.txt'):
                    file_path = os.path.join(sub_dir_path, file_name)
                    pubmed_tag = f"{sub_dir_name}\t{file_name.replace(' ', '_')}"
                    print(f"Processing: {pubmed_tag}")
                    Txt2ShortHz(file_path, pubmed_tag)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <directory>")
    else:
        ManyFileTxt2FormatMod3(sys.argv[1])
