ToricCam 1.0.0 - README file                   26 July 2015
===========================================================

ToricCam is a C++ library for intuitive and efficient camera control in a 3D scene, by working directly on the set of visual properties on one or two targets.
Visual properties that can be accounted for are the targets' on-screen positions, sizes, distances to camera, or vantage angles.
The library is released under the GNU GPL license.
Source code is available at https://sites.google.com/site/christophelino/libraries/toric-cam/

This library was written by Christophe Lino (https://sites.google.com/site/christophelino/).
If you use the library in any application or project, please drop me a line at christophe.lino@inria.fr

Copyright (c) 2015 Christophe Lino

Besides the library source code, we also provide sample code for examples explaining how the library can be used to compute classical viewpoints in cinematography.
We also provide methods to connect the library to the Ogre rendering engine, which serves as an example of how the library can easily be plug in any other rendering engine.
The "OgreConnection.h" file provides all code to connect the library to Ogre. You can modify the code in that file to connect the library to other rendering engines.  

See the readme files in the Samples directory for details on the example applications code.

---------------

ToricCam is a free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

CREDITS:

----------------

OGRE (www.ogre3d.org) is made available under the MIT License.

Copyright (c) 2000-2009 Torus Knot Software Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.