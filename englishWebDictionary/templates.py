"""This module defines various templates that is used in model."""

CSS = '''
.card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}

.big {
  font-size: 48px;
}

.med {
  font-size: 28px;
}

.medsmall {
  font-size: 22px;
}

.small {
  font-size: 18px;
}

.bottom {
  display: block;
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
}
'''

CARD_TEMPLATES = [
    {'name': 'Word -> definition',

     'question': '''
<div class="big" id="Head">
    {{%(lettering)s}}
</div>

<div class="small">
    {{#%(hint)s}}{{hint:%(hint)s}}{{/%(hint)s}}
</div>

<div class="small">
    {{hint:%(context)s}}
</div>

{{#%(partOfSpeech)s}}
    <div class="bottom small">
        {{hint:%(partOfSpeech)s}}
    </div>
{{/%(partOfSpeech)s}}
''',

     'answer': '''
<div class="big" id="Head">
    {{%(lettering)s}}
    {{#%(hint)s}}({{%(hint)s}}){{/%(hint)s}}
</div>

</br>

<div class="small">
    {{%(context)s}}
</div>

{{#%(partOfSpeech)s}}
    <div class="small">
        <i>{{%(partOfSpeech)s}}</i>
    </div>
{{/%(partOfSpeech)s}}

<hr id=answer>

<div class="medsmall">
    {{#%(transcription)s}}[{{%(transcription)s}}]{{/%(transcription)s}}
</div>

</br>
</br>

{{#%(definition)s}}
    <div classs="small">
        <u>Meaning:</u>
        </br>
        {{%(definition)s}}
    </div>
{{/%(definition)s}}

</br>

{{#%(example)s}}
    <div classs="small">
        <u>Example:</u>
        </br>
        {{%(example)s}}
    </div>
{{/%(example)s}}
'''},


    {'name': 'Definition -> word',

     'question':  '''
<div classs="med" id="Head">
    <u>Meaning:</u>
    </br>
    {{%(definition)s}}
</div>
''',

     'answer': '''
<div classs="med" id="Head">
    <u>Meaning:</u>
    </br>
    {{%(definition)s}}
</div>

<hr id=answer>

<div class="big" id="Head">
    {{%(lettering)s}}
    {{#%(hint)s}}({{%(hint)s}}){{/%(hint)s}}
</div>

</br>

<div class="small">
    {{%(context)s}}
</div>

{{#%(partOfSpeech)s}}
    <div class="small">
        <i>{{%(partOfSpeech)s}}</i>
    </div>
{{/%(partOfSpeech)s}}

</br>

<div class="medsmall">
    {{#%(transcription)s}}[{{%(transcription)s}}]{{/%(transcription)s}}
</div>

</br>

{{#%(example)s}}
    <div classs="small">
        <u>Example:</u>
        </br>
        {{%(example)s}}
    </div>
{{/%(example)s}}
'''}
]
