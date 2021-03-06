"use strict"
var restful = require('node-restful')
var mongoose = restful.mongoose;


var imageSchema =  new mongoose.Schema({

    // Information  only of the Taggged Images
    name:      { // <repo:tag> the name id composed by: repository name : tag
        type:       String,
        unique:     true,
        required    :[true, 'The name of the image cannot be empty']
    },
    id_tag: Number,
    last_scan:      Date,
    last_updated:   Date,  // time of the last updated of the repo in the docker hub
    size:      Number,
    repository: Number,
    creator: Number,

    //Docker repository informations
    user:String,
    stars:     {
        type:       Number,
        min:        [0, 'stars must be positive number']
    },
    pulls:     Number,
    description:    String,
    is_automated: Boolean,
    is_private: Boolean,

    //Docker Finder informations
    distro:     String,
    softwares:       [{
        _id: false,
        software: String,
        ver: String
    }],

    status: String, // "pending" | "updated": if pending the image description must be updated.

    inspect_info:  mongoose.Schema.Types.Mixed  // docker run inpect <name> 

});


// Return a model
module.exports = restful.model("Images",imageSchema);
