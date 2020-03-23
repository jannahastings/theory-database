

#import numpy as np
#import pandas as pd
#from os import path
#from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt
#% matplotlib inline

for theory in theories.values():
    # Create and generate a word cloud image:
    wordcloud = WordCloud(background_color="white").generate(" ".join([c.name.replace("'","") for c in theory.constructs.values()]))

    # Display the generated image:
    plt.figure( figsize=(6,3) )
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("static/"+theory.number+"-wc.png")
    plt.close()

