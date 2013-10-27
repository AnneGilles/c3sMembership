The Slider in the membership application form is built with jquery.

You need to patch your local deform widgets.py
and add a slider named `slider.pt`.

To widgets.py add a class **TextInputSliderWidget** similar to
**TextInputWidget** like so::

  class TextInputSliderWidget(Widget):
  """
  renders a slider widget using jquery
  """
  template = 'slider'


Depending on your setup, you find the files under::

   env/lib/python2.7/site-packages/deform-0.9.8-py2.7.egg/deform/widget.py


The template can be put under 'deform/templates/slider.pt'
and it could look like so::

    1<span tal:define="name name|field.name;
    2                  size size|field.widget.size;
    3                  css_class css_class|field.widget.css_class;
    4                  oid oid|field.oid;
    5                  mask mask|field.widget.mask;
    6                  mask_placeholder mask_placeholder|field.widget.mask_placeholder;
    7                  style style|field.widget.style|None;
    8                  "
    9      tal:omit-tag="">
    10<script type="text/javascript">
    11$(function() {
    12  $( "#slider-div-num_shares" ).slider({
    13    range: "max",
    14    min: 1,
    15    max: 60,
    16    value: ${cstruct},
    17    slide: function( event, ui ) {
    18      $( "#num_shares" ).val( ui.value );
    19      $( "#num_shares-calculated" ).val( ui.value * 50 );
    20    }
    21  });
    22  $( "#num_shares" ).val( $( "#slider-div-num_shares" ).slider( "value" ) );
    23});
    24</script>
    25  <input type="text" name="${name}" value="${cstruct}"
    26         tal:attributes="size size;
    27                         class css_class;
    28                         style style"
    29         id="${oid}"/>
    30  (= <input type="text" name="${name}-calculated" value="${int(cstruct)*50}"
    31         tal:attributes="size size;
    32                         class css_class;
    33                         style style"
    34         id="${oid}-calculated"/>€)
    35
    36  <div id="slider-div-${oid}"></div><br />
    37  <script tal:condition="mask" type="text/javascript">
    38    deform.addCallback(
    39    '${oid}',
    40    function (oid) {
    41    $("#" + oid).mask("${mask}",
    42    {placeholder:"${mask_placeholder}"});
    43    });
    44  </script>
    45</span>

Note that this will show a second text input used to show
a calculated number -- shares times fifty -- the product.
