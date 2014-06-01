"""
Image Tag
---------
This implements a Liquid-style image tag for Pelican,
based on the octopress image tag [1]_

Syntax
------
{% img [class name(s)] [http[s]:/]/path/to/image [width] [title text | "title text" ["alt text"] ["caption"] %}

Examples
--------
{% img /images/ninja.png Ninja Attack! %}
{% img left half http://site.com/images/ninja.png Ninja Attack! %}
{% img left half http://site.com/images/ninja.png 150 150 "Ninja Attack!" "Ninja in attack posture" "Picture of a Ninja"%}

Output
------
<div class="figure" style="width: 484px; height: auto">
<img src="/images/ninja.png">
</div>

<div class="figure left half" style="width: 484px; height: auto">
<img class="left half" src="http://site.com/images/ninja.png" title="Ninja Attack!" alt="Ninja Attack!">
</div>

<div class="figure left half" style="width: 150px; height: auto">
<img class="left half" style="width: 150px height: auto;"
src="http://site.com/images/ninja.png" title="Ninja Attack!" alt="Ninja in
attack posture">
<p class="caption">Picture of a Ninja!<p>
</div

[1] https://github.com/imathis/octopress/blob/master/plugins/image_tag.rb
"""
import os
import re
from PIL import Image
from .mdx_liquid_tags import LiquidTags

SYNTAX = '{% img [class name(s)] [http[s]:/]/path/to/image [width [height]] [title text | "title text" ["alt text"]] %}'

# Regular expression to match the entire syntax
ReImg = re.compile("""(?P<class>\S.*\s+)?(?P<src>(?:https?:\/\/|\/|\S+\/)\S+)(?:\s+(?P<width>\d+))?(?:\s+(?P<height>\d+))?(?P<title>\s+.+)?""")

# Regular expression to split the title and alt text
ReTitleAlt = re.compile("""(?:"|')(?P<title>[^"']+)?(?:"|')\s+(?:"|')(?P<alt>[^"']+)?(?:"|')""")
ReTitleAltCap = re.compile("""(?:"|')(?P<title>[^"']+)?(?:"|')\s+(?:"|')(?P<alt>[^"']+)?(?:"|')\s+(?:"|')(?P<caption>[^"']+)?(?:"|')""")

@LiquidTags.register('img')
def img(preprocessor, tag, markup):
    attrs = None

    # Parse the markup string
    match = ReImg.search(markup)
    if match:
        attrs = dict([(key, val.strip())
                      for (key, val) in match.groupdict().iteritems() if val])
    else:
        raise ValueError('Error processing input. '
                         'Expected syntax: {0}'.format(SYNTAX))

    # Check if alt text is present -- if so, split it from title
    if 'title' in attrs:
        match = ReTitleAltCap.search(attrs['title'])
        if match:
            attrs.update(match.groupdict())
        if not attrs.get('alt'):
            attrs['alt'] = attrs['title']

    img_path = ''
    if attrs['src'].startswith('/'):
        img_path = attrs['src'][1:]
    else:
        img_path = attrs['src']
    settings = preprocessor.configs.config['settings']
    img_path = os.path.join('content', img_path)
    if not os.path.exists(img_path):
        raise ValueError("File {0} could not be found".format(img_path))


    #If no width specified
    if not 'width' in attrs:
        im = Image.open(img_path)
        attrs['width'] = im.size[0]
        attrs['height'] = 'auto'


    cls = ""
    if  attrs.get('class'):
        cls = attrs['class']

    extra_style = 'width: {}px; height: auto;'.format(attrs['width'])

    open_tag = None
    fig_Tag = None
    close_tag = None

    open_tag = ('<div class="figure {cls}" style="{extra_style}">'.format(
        cls=attrs['class'],
        extra_style=extra_style))

    close_tag = ("</div>")

    imagetag = ('<img class="{cls}" style="width: {width}px height: auto;" alt="{alt}" '
            'title="{title}" src="{src}">'.format(cls=cls, width=attrs['width'], alt=attrs['alt'],
                    title=attrs['title'], src=attrs['src']))

    source = None
    if attrs.get('caption'):
        fig_tag = ('{imagetag}\n <p class="caption">{captiontext}</p>'.format(
                        imagetag=imagetag,
                        captiontext=attrs.get('caption')))

        source = (open_tag + '\n' +fig_tag + '\n' + close_tag)
    else:
        source = (open_tag + '\n' + imagetag + '\n'+ close_tag)

    return source



#----------------------------------------------------------------------
# This import allows image tag to be a Pelican plugin
from liquid_tags import register

