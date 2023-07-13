import en_core_web_sm
import nltk
import pandas as pd
from nltk import sent_tokenize
import pyinflect
from generators.piplines import TaskGenerator

nltk.download('punkt')
nlp = en_core_web_sm.load()


def basic_clean(text: str):
    return text.replace('\n\n', '.\n').replace('".', '"').replace('..', '.').replace('pp.', 'pp')


def pos_tag(text):
    doc = nlp(text)
    result = dict()
    for num, token in enumerate(doc):
        result[num] = {'token': token, 'pos': token.pos_}

    return result


def make_df(text: str):
    text = basic_clean(text)
    txt = sent_tokenize(text, language="english")
    df = pd.DataFrame(txt, columns=["sentence"])
    df["sentence"].str.strip()

    df['sentence_schema'] = df['sentence'].apply(lambda x: pos_tag(x))
    df['tokens'] = df['sentence_schema'].apply(lambda x: [elem['token'] for elem in x.values()])
    return df


if __name__ == '__main__':
    txt = '''
    Little Red Riding Hood

Charles Perrault

Once upon a time there lived in a certain village a little country girl, the prettiest creature who was ever seen. Her mother was excessively fond of her; and her grandmother doted on her still more. This good woman had a little red riding hood made for her. It suited the girl so extremely well that everybody called her Little Red Riding Hood.
One day her mother, having made some cakes, said to her, "Go, my dear, and see how your grandmother is doing, for I hear she has been very ill. Take her a cake, and this little pot of butter."

Little Red Riding Hood set out immediately to go to her grandmother, who lived in another village.

As she was going through the wood, she met with a wolf, who had a very great mind to eat her up, but he dared not, because of some woodcutters working nearby in the forest. He asked her where she was going. The poor child, who did not know that it was dangerous to stay and talk to a wolf, said to him, "I am going to see my grandmother and carry her a cake and a little pot of butter from my mother."

"Does she live far off?" said the wolf
    '''
    df = (make_df(txt))
    gen = TaskGenerator(df)
    res = gen.run_pipeline()
    print(gen.get_tasks_types())
    print(res)
