/**
 *
 * HeatTop JS Framework
 * Dependencies: jQuery 1.7.1 or later, KineticJS 4.5.2 or later
 * Date: June 2013
 * Description: JS Framework that subclasses the KineticJS library to create
 * Heat-specific objects and relationships with the purpose of displaying
 * Stacks, Resources, and related Properties in a Resource Topology Graph.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
   not use this file except in compliance with the License. You may obtain
   a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
   License for the specific language governing permissions and limitations
   under the License.
*/

var Heat = {
    Stage:Stage,
    Layer:Layer,
    Group:Group,
    Stack:Stack,
    Resource:Resource,
    rowHeight:150,  //Each Sub-Dependency should be in a subsequent row of its Super,
                    // Nbr of rows depends on Nbr of Dependencies
    colors:{
      success:'#0e630e',
      successFill:'#daedda',
      pending:'yellow',
      pendingFill:'darkyellow',
      failed:'darkred',
      failedFill:'#f4e8e8',
      neutral:'#353535',
      neutralFill:'#ddd',
    },
}

function Stage(options){
    return new Kinetic.Stage(options);
}

function Layer(options){
    return new Kinetic.Layer(options);
}

function Group(options){
    return new Kinetic.Group(options);
}

function Stack(options){

    loadImages(sources, function(images) {
        return draw(images);
      });

    function draw(images){
        var stack = options.stack;
        var stage = options.stage;
        var layer = options.layer;

        //Define width of rectangle
        var rect_width = 500;

        var group = new Heat.Group({
            x: (stage.getWidth()/2) - (rect_width/2),
            y: 10
        });

        var rect = new Kinetic.Rect({
            width: rect_width,
            height: 100,
            stroke: check_state(stack.stack_status),
            strokeWidth: 2,
            fill: check_state(stack.stack_status, true),
            shadowColor: 'black',
            shadowBlur: 10,
            shadowOffset: [5, 5],
            shadowOpacity: 0.2,
            cornerRadius: 10
        });

        var gradientRect = new Kinetic.Rect({
           width:rect.getWidth(),
           height:rect.getHeight(),
           cornerRadius: 10,
           fillPatternImage: images.gradient,
        });

        var stack_name = new Kinetic.Text({
            text: stack.stack_name,
            fontSize: 20,
            fontStyle:'bold',
            fontFamily: 'Calibri',
            fill: Heat.colors.neutral,
            padding: 5
        });

        var state_text = '';
        if (stack.stack_status_reason != ''){
            state_text = stack.stack_status + ': ' + stack.stack_status_reason;
        } else {
            state_text = stack.stack_status;
        }
        var stack_state = new Kinetic.Text({
            //x: stack_name.getPosition().x + stack_name.getWidth(),
            y: 6,
            width:rect.getWidth(),
            text: state_text,
            fontSize: 14,
            fontStyle:'bold',
            fontFamily: 'Calibri',
            fill: check_state(stack.stack_status),
            padding: 5,
            align:'right',
        });

        var stack_desc = new Kinetic.Text({
            y:stack_name.getPosition().y + stack_name.getHeight(),
            width:rect.getWidth(),
            height:rect.getHeight() - stack_name.getHeight(),
            text: stack.description,
            fontSize: 11,
            fontStyle:'normal',
            fontFamily: 'Calibri',
            fill: Heat.colors.neutral,
            padding: 5
        });



        // add the shapes to the group
        group.add(rect);
        group.add(gradientRect);
        group.add(stack_name);
        group.add(stack_state);
        group.add(stack_desc);

        layer.add(group);
        stage.add(layer);

        return group
    }


}

function Resource(options){

    loadImages(sources, function(images) {
        return draw(images);
    });

    function draw(images){
        var resource = options.resource;
        var stage = options.stage;
        var layer = options.layer;

        //Define width of rectangle
        var rect_width = 150;

        var group = new Heat.Group({
            x: (stage.getWidth()/2) - (rect_width/2),
            y: 10
        });

        var rect = new Kinetic.Rect({
            width: rect_width,
            height: 100,
            stroke: check_state(resource.resource_status),
            strokeWidth: 2,
            fill: check_state(resource.resource_status, true),
            shadowColor: 'black',
            shadowBlur: 10,
            shadowOffset: [5, 5],
            shadowOpacity: 0.2,
            cornerRadius: 10
        });

        var gradientRect = new Kinetic.Rect({
           width:rect.getWidth(),
           height:rect.getHeight(),
           cornerRadius: 10,
           fillPatternImage: images.gradient,
        });


        var resource_name = new Kinetic.Text({
            width:rect_width,
            height:14,
            text: resource.logical_resource_id,
            fontSize: 14,
            fontStyle:'bold',
            fontFamily: 'Calibri',
            fill: Heat.colors.neutral,
            padding: 5
        });

        var state_text = '';
        if (resource.resource_status_reason != ''){
            state_text = resource.resource_status + ':';
        } else {
            state_text = resource.resource_status;
        }
        var resource_state = new Kinetic.Text({
            y: resource_name.getPosition().y + resource_name.getHeight() + 5,
            width:rect.getWidth(),
            height:12,
            text: state_text,
            fontSize: 12,
            fontStyle:'bold',
            fontFamily: 'Calibri',
            fill: check_state(resource.resource_status),
            padding: 5,
        });
        var state_reason = false;
        var resource_type_y = resource_state.getPosition().y + resource_state.getHeight();
        if (resource.resource_status_reason != ''){
            state_reason = new Kinetic.Text({
                y: resource_state.getPosition().y + resource_state.getHeight(),
                width:rect.getWidth(),
                height:12,
                text: resource.resource_status_reason,
                fontSize: 12,
                fontStyle:'bold',
                fontFamily: 'Calibri',
                fill: check_state(resource.resource_status),
                padding: 5,
            });
            resource_type_y =state_reason.getPosition().y + state_reason.getHeight()
        }

        var resource_type = new Kinetic.Text({
            y:resource_type_y + 5,
            width:rect.getWidth(),
            height:rect.getHeight() - resource_name.getHeight(),
            text: resource.resource_type,
            fontSize: 11,
            fontStyle:'normal',
            fontFamily: 'Calibri',
            fill: Heat.colors.neutral,
            padding: 5
        });

        // add the shapes to the layer
        group.add(rect);
        group.add(gradientRect);
        group.add(resource_name);
        group.add(resource_state);
        if (state_reason != false){group.add(state_reason)}
        group.add(resource_type);

        layer.add(group);
        stage.add(layer);
        return group

    }
}

function check_state(state, fill){
    fill = typeof fill !== 'undefined' ? fill : false

    if (state == 'CREATE_FAILED'){
        if (fill){return Heat.colors.failedFill;}
        else{return Heat.colors.failed;}
    } else if (state == 'CREATE_IN_PROGRESS'){
        if (fill){return Heat.colors.pendingFill;}
        else{return Heat.colors.pending;}
    } else if (state == 'CREATE_COMPLETE'){
        if (fill){return Heat.colors.successFill;}
        else{return Heat.colors.success;}
    } else {
      if (fill){return Heat.colors.neutralFill;}
        else{return Heat.colors.neutral;}
    }
}

var sources = {
    darthVader: 'http://www.html5canvastutorials.com/demos/assets/darth-vader.jpg',
    yoda: 'http://www.html5canvastutorials.com/demos/assets/yoda.jpg',
    gradient: '/static/heat/img/topGradient.png',
};

function loadImages(sources, callback) {
    var images = {};
    var loadedImages = 0;
    var numImages = 0;
    // get num of sources
    for(var src in sources) {
      numImages++;
    }
    for(var src in sources) {
      images[src] = new Image();
      images[src].onload = function() {
        if(++loadedImages >= numImages) {
          callback(images);
        }
      };
      images[src].src = sources[src];
    }
}

