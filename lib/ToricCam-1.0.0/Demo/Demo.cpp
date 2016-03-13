/*
 * TestToric
 *
 * Test Cases for the Toric Camera Solver
 */

#include "SingleTarget.h"
#include "TwoTargets.h"
#include "TargetOOBB.h"
#include "TargetOOBS.h"
#include <toric\Quaternion.h>
#include <toric\Vector.h>
#include <iostream>
#include <string>

using namespace toric;
using namespace samples;

/***************************************************************************************************/
/// \brief	Initializes attributes of given actor, abstracted as a bounding sphere
///
/// \author	Christophe Lino and William Bares
/// \date	2015/07/26
///
///	\param[in] actor	Given actor approximated by bounding sphere.
///	\param[in] posX		Position x-coordinate
///	\param[in] posY		Position y-coordinate
/***************************************************************************************************/

void initSphereActor(TargetOOBS& actor, float posX, float posY)
{
  // Radius of bounding sphere.
  actor.radius = 1.0f;

  // Set location of center of bounding sphere.
  actor.position[0] = posX;
  actor.position[1] = posY;
  actor.position[2] = actor.radius;

  std::cout << "Actor Position: (" << actor.position.x() << ", " << actor.position.y() << ", " << actor.position.z() << ")" << std::endl;
  std::cout << "Actor radius: " << actor.radius << std::endl;

  // Assume at-rest character model has
  // +Z-up, +Y-front, and +X as extended right hand.
  // Specify rotation applied to at-rest actor.
  // Give the unit quaternion that leaves the actor at-rest.
  actor.orientation.set(1.0f, Vector3(0, 0, 0));

  std::cout << "Actor Orientation: (x,y,z,w) = (" << actor.orientation.x() << ", " << actor.orientation.y() << ", " << actor.orientation.z() <<
    ", " << actor.orientation.w() << ")" << std::endl << std::endl;
}

/***************************************************************************************************/
/// \brief	Initializes attributes of given actor, abstracted as an OOBB
///
/// \author	Christophe Lino and William Bares
/// \date	2015/07/26
///
///	\param[in] actor	Given actor approximated by bounding sphere.
///	\param[in] posX		Position x-coordinate
///	\param[in] posY		Position y-coordinate
/***************************************************************************************************/

void initBoxActor(TargetOOBB& actor, float posX, float posY)
{
  // dimensions of bounding box.
  actor.dimension = Vector3(1.0f,1.0f,1.0f);

  // Set location of center of bounding sphere.
  actor.position[0] = posX;
  actor.position[1] = posY;
  actor.position[2] = actor.dimension.z();

  std::cout << "Actor Position: (" << actor.position.x() << ", " << actor.position.y() << ", " << actor.position.z() << ")" << std::endl;
  std::cout << "Actor Dimension: (" << actor.dimension.x() << ", " << actor.dimension.y() << ", " << actor.dimension.z() << ")" << std::endl;

  // Assume at-rest character model has
  // +Z-up, +Y-front, and +X as extended right hand.
  // Specify rotation applied to at-rest actor.
  // Give the unit quaternion that leaves the actor at-rest.
  actor.orientation.set(1.0f, Vector3(0, 0, 0));

  std::cout << "Actor Orientation: (x,y,z,w) = (" << actor.orientation.x() << ", " << actor.orientation.y() << ", " << actor.orientation.z() <<
    ", " << actor.orientation.w() << ")" << std::endl << std::endl;
}

/***************************************************************************************************/
/// \brief	Runs a test case for single subject Toric camera solver.
///
/// \author	Christophe Lino and William Bares
/// \date	2015/07/26
///
///	\param[in] screenX		Given desired projection x-coordinate.
///	\param[in] screenY		Given desired projection y-coordinate.
///	\param[in] fovX			Camera field of view angle given in radians.
///	\param[in] hAngle		horizontal angle in radians.
///	\param[in] vAngle		vertical angle in radians.
/***************************************************************************************************/

void testSingle(float screenX, float screenY, const RadianPi& fovX, 
  const RadianPi& hAngle, const RadianPi& vAngle)
{
  std::cout << "---------------- Test Case Single Target (Box) -----------------" << std::endl;

  // Assume World Coordinate System is right-handed, Z-up and Y-front.

  // Approximate the actor using a bounding box.
  {
	  TargetOOBB actor;

	  // Initialze actor (unit box) at (0,0,dimension) and unit quaternion orientation.
	  initBoxActor(actor, 0.0f, 0.0f);

	  // Aspect ratio of screen width divided by height.
	  float screenAspect = 1.0f;
	  // Desired projection location on screen having bottom-left (-1,-1), center(0,0), and top-right(1,1).
	  Vector2 screenPos(screenX, screenY);
	  // Desired projected on-screen height of actor's bounding sphere.
	  // Total screen height is 2.0 units.
	  float screenHeight = 1.0f;

	  std::cout << "Horizontal field of view angle spans full width of frustum given in degrees: " << fovX.valueDegrees() << std::endl;
	  std::cout << "Screen aspect ratio: " << screenAspect << std::endl;
	  std::cout << "Desired projected screen location of actor's center: (" << screenPos[0] << ", " << screenPos[1] << ")" << std::endl;
	  std::cout << "Desired projected height of actor: " << screenHeight << std::endl << std::endl;

	  std::cout << "Screen has coordinates of bottom-left (-1,-1), center(0,0), and top-right(1,1)." << std::endl << std::endl;

	  std::cout << "Constructing toric surface for one target..." << std::endl;
	  SingleBoxTargetProblem toricSingle(fovX, screenAspect, actor, screenPos, screenHeight);

	  std::cout << "H Angle in degrees: " << hAngle.valueDegrees() << std::endl;
	  std::cout << "V Angle in degrees: " << vAngle.valueDegrees() << std::endl;

	  std::cout << "Computing viewpoint from angles..." << std::endl;
	  const Camera& cam = toricSingle.ComputeViewpointFromVantage(hAngle, vAngle);

	  std::cout << "Position: (" << cam.position.x() << ", " << cam.position.y() << ", " << cam.position.z() << ")" << std::endl;
	  std::cout << "Orientation: (x,y,z,w) = (" << cam.orientation.x() << ", " << cam.orientation.y() << ", " << cam.orientation.z() <<
		", " << cam.orientation.w() << ")" << std::endl;

	  TargetOOBB::VisualFeatures features = actor.GetVisualFeaturesFromViewpoint(cam);
	  std::cout << "Actor's top screen position: (" << features.screenPositionTop.x() << ", " << features.screenPositionTop.y() << ")" << std::endl;
	  std::cout << "Actor's bottom screen position: (" << features.screenPositionBottom.x() << ", " << features.screenPositionBottom.y() << ")" << std::endl;
	  std::cout << "Actor's screen height: " << (features.screenPositionTop.y() - features.screenPositionBottom.y()) * 0.5 << std::endl;
	  std::cout << "Actor's vantage (H/V in degrees): (" << features.horizontalAngle.valueDegrees() << ", " << features.verticalAngle.valueDegrees() <<  ")" << std::endl;
  }

  std::cout << "---------------- Test Case Single Target (Sphere) -----------------" << std::endl;

  {
	  TargetOOBS actor;

	  // Initialize actor (unit sphere) at (0,0,radius) and unit quaternion orientation.
	  initSphereActor(actor, 0.0f, 0.0f);

	  // Aspect ratio of screen width divided by height.
	  float screenAspect = 1.0f;
	  // Desired projection location on screen having bottom-left (-1,-1), center(0,0), and top-right(1,1).
	  Vector2 screenPos(screenX, screenY);
	  // Desired projected on-screen height of actor's bounding sphere.
	  // Total screen height is 2.0 units.
	  float screenHeight = 1.0f;

	  std::cout << "Horizontal field of view angle spans full width of frustum given in degrees: " << fovX.valueDegrees() << std::endl;
	  std::cout << "Screen aspect ratio: " << screenAspect << std::endl;
	  std::cout << "Desired projected screen location of actor's center: (" << screenPos[0] << ", " << screenPos[1] << ")" << std::endl;
	  std::cout << "Desired projected height of actor: " << screenHeight << std::endl << std::endl;

	  std::cout << "Screen has coordinates of bottom-left (-1,-1), center(0,0), and top-right(1,1)." << std::endl << std::endl;

	  std::cout << "Constructing toric surface for one target..." << std::endl;
	  SingleSphereTargetProblem toricSingle(fovX, screenAspect, actor, screenPos);

	  std::cout << "H Angle in degrees: " << hAngle.valueDegrees() << std::endl;
	  std::cout << "V Angle in degrees: " << vAngle.valueDegrees() << std::endl;

	  std::cout << "Computing viewpoint from angles..." << std::endl;
	  const Camera& cam = toricSingle.ComputeViewpointFromScreenHeightAndVantage(screenHeight, hAngle, vAngle);

	  std::cout << "Position: (" << cam.position.x() << ", " << cam.position.y() << ", " << cam.position.z() << ")" << std::endl;
	  std::cout << "Quaternion: (x,y,z,w) = (" << cam.orientation.x() << ", " << cam.orientation.y() << ", " << cam.orientation.z() <<
		  ", " << cam.orientation.w() << ")" << std::endl;

	  TargetOOBS::VisualFeatures features = actor.GetVisualFeaturesFromViewpoint(cam);
	  std::cout << "Actor's screen position: (" << features.screenPosition.x() << ", " << features.screenPosition.y() << ")" << std::endl;
	  std::cout << "Actor's screen height: " << features.screenHeight << std::endl;
	  std::cout << "Actor's vantage (H/V in degrees): (" << features.horizontalAngle.valueDegrees() << ", " << features.verticalAngle.valueDegrees() <<  ")" << std::endl;
  }

  std::cout << "------------------------------------------------" << std::endl;

  std::string str;
  std::cerr << "Entry anything to continue...";
  std::cin >> str;
}

/***************************************************************************************************/
/// \brief	Runs a test case for double subject Toric camera solver.
///
/// \author	Christophe Lino and William Bares
/// \date	2015/07/26
///
///	\param[in] screenX1		Given desired projection x-coordinate.
///	\param[in] screenY1		Given desired projection y-coordinate.
///	\param[in] screenX2		Given desired projection x-coordinate.
///	\param[in] screenY2		Given desired projection y-coordinate.
///	\param[in] fovX		Camera field of view angle given in radians.
///	\param[in] hAngle	horizontal angle in radians.
///	\param[in] vAngle	vertical angle in radians.
/***************************************************************************************************/

void testDouble(float screenX1, float screenY1, float screenX2, float screenY2,
  const RadianPi& fovX,
  const RadianPi& hAngle, const RadianPi& vAngle)
{
  std::cout << "---------------- Test Case Two Targets -----------------" << std::endl;

  // Assume World Coordinate System is right-handed, Z-up and Y-front.

  // Approximate the actor using a bounding sphere.
  TargetOOBS actor1, actor2;

  // Initialze actor (unit sphere) at (-2,0,radius) and unit quaternion orientation.
  initSphereActor(actor1, -2.0f, 0.0f);

  // Initialze actor (unit sphere) at (+2,0,radius) and unit quaternion orientation.
  initSphereActor(actor2, 2.0f, 0.0f);

  // Aspect ratio of screen width divided by height.
  float screenAspect = 1.0f;
  // Desired projection location on screen having bottom-left (-1,-1), center(0,0), and top-right(1,1).
  Vector2 screenPos1(screenX1, screenY1);
  Vector2 screenPos2(screenX2, screenY2);

  // Desired projected on-screen height of actor's bounding sphere.
  // Total screen height is 2.0 units.
  float screenHeight = 1.0f;

  std::cout << "Horizontal field of view angle spans full width of frustrum given in degrees: " << fovX.valueDegrees() << std::endl;
  std::cout << "Screen aspect ratio: " << screenAspect << std::endl;
  std::cout << "Desired projected screen location of first actor's center: (" << screenPos1[0] << ", " << screenPos1[1] << ")" << std::endl;
  std::cout << "Desired projected screen location of second actor's center: (" << screenPos2[0] << ", " << screenPos2[1] << ")" << std::endl;

  std::cout << "Desired projected height of first actor: " << screenHeight << std::endl << std::endl;

  std::cout << "Screen has coordinates of bottom-left (-1,-1), center(0,0), and top-right(1,1)." << std::endl << std::endl;

  std::cout << "Constructing toric surface for two targets..." << std::endl;
  TwoSphereTargetProblem toricDouble(fovX, screenAspect, actor1, actor2, screenPos1, screenPos2);

  std::cout << "H Angle in degrees: " << hAngle.valueDegrees() << std::endl;
  std::cout << "V Angle in degrees: " << vAngle.valueDegrees() << std::endl;

  // Assume first target is featured for view angle and height in screen.
  {
	  std::cout << "Computing viewpoint to optimize screen position and height of first actor..." << std::endl;
	  
	  const Camera& camH = toricDouble.ComputeViewpointFromScreenHeight(screenHeight, TwoSphereTargetProblem::Target1);

	  std::cout << "Position: (" << camH.position.x() << ", " << camH.position.y() << ", " << camH.position.z() << ")" << std::endl;
	  std::cout << "Quaternion: (x,y,z,w) = (" << camH.orientation.x() << ", " << camH.orientation.y() << ", " << camH.orientation.z() <<
		  ", " << camH.orientation.w() << ")" << std::endl;
	  
	  std::cout << std::endl;
	  std::cout << "Here are the visual features corresponding to this viewpoint:" << std::endl;

	  TargetOOBS::VisualFeatures features1 = actor1.GetVisualFeaturesFromViewpoint(camH);
	  std::cout << "Actor #1 screen position: (" << features1.screenPosition.x() << ", " << features1.screenPosition.y() << ")" << std::endl;
	  std::cout << "Actor #1 screen height: " << features1.screenHeight << std::endl;
	  std::cout << "Actor #1 vantage (H/V in degrees): (" << features1.horizontalAngle.valueDegrees() << ", " << features1.verticalAngle.valueDegrees() <<  ")" << std::endl;
	  std::cout << "---" << std::endl;
	  TargetOOBS::VisualFeatures features2 = actor2.GetVisualFeaturesFromViewpoint(camH);
	  std::cout << "Actor #2 screen position: (" << features2.screenPosition.x() << ", " << features2.screenPosition.y() << ")" << std::endl;
	  std::cout << "Actor #2 screen height: " << features2.screenHeight << std::endl;
	  std::cout << "Actor #2 vantage (H/V in degrees): (" << features2.horizontalAngle.valueDegrees() << ", " << features2.verticalAngle.valueDegrees() <<  ")" << std::endl;
  }
  std::cout << std::endl;
  {
	  std::cout << "Computing viewpoint to optimize screen position and at view angle of first actor..." << std::endl;

	  const Camera& camV = toricDouble.ComputeViewpointFromVantage(hAngle, vAngle, TwoSphereTargetProblem::Target1);

	  std::cout << "Position: (" << camV.position.x() << ", " << camV.position.y() << ", " << camV.position.z() << ")" << std::endl;
	  std::cout << "Quaternion: (x,y,z,w) = (" << camV.orientation.x() << ", " << camV.orientation.y() << ", " << camV.orientation.z() <<
		  ", " << camV.orientation.w() << ")" << std::endl;

	  std::cout << std::endl;
	  std::cout << "Here are the visual features corresponding to this viewpoint:" << std::endl;

	  TargetOOBS::VisualFeatures features1 = actor1.GetVisualFeaturesFromViewpoint(camV);
	  std::cout << "Actor #1 screen position: (" << features1.screenPosition.x() << ", " << features1.screenPosition.y() << ")" << std::endl;
	  std::cout << "Actor #1 screen height: " << features1.screenHeight << std::endl;
	  std::cout << "Actor #1 vantage (H/V in degrees): (" << features1.horizontalAngle.valueDegrees() << ", " << features1.verticalAngle.valueDegrees() <<  ")" << std::endl;
	  std::cout << "---" << std::endl;
	  TargetOOBS::VisualFeatures features2 = actor2.GetVisualFeaturesFromViewpoint(camV);
	  std::cout << "Actor #2 screen position: (" << features2.screenPosition.x() << ", " << features2.screenPosition.y() << ")" << std::endl;
	  std::cout << "Actor #2 screen height: " << features2.screenHeight << std::endl;
	  std::cout << "Actor #2 vantage (H/V in degrees): (" << features2.horizontalAngle.valueDegrees() << ", " << features2.verticalAngle.valueDegrees() <<  ")" << std::endl;
  }

  std::cout << "------------------------------------------------" << std::endl;

  std::string str;
  std::cerr << "Entry anything to continue...";
  std::cin >> str;
}

double rand(double min, double max)
{
	return (max-min) * rand() / double( RAND_MAX ) + min;
}

/***************************************************************************************************/
/// \brief	Main function. Launches both test cases on single and double subject configurations
///
/// \author	Christophe Lino and William Bares
/// \date	2015/07/26
/***************************************************************************************************/

int main()
{
	//---------- Single Actor Test Cases -------------------
	for(size_t i=0; i<10; i++) // random cases
	{
		RadianPi fovX(rand(10,60) * DegToRad);
		RadianPi hAngle(rand(-180,+180) * DegToRad);
		RadianPi vAngle(rand(-89,+89) * DegToRad);
		float x = rand(-1,+1), y = rand(-1,+1);
		testSingle(x, y, fovX, hAngle, vAngle);
	}

	RadianPi hAngle1(0.0f);
	RadianPi vAngle(0.0f);

	RadianPi fov10(10.0f * DegToRad);
	testSingle(0.0f, 0.0f, fov10, hAngle1, vAngle);

	RadianPi fov20(20.0f * DegToRad);
	testSingle(0.0f, 0.0f, fov20, hAngle1, vAngle);

	RadianPi fov30(30.0f * DegToRad);
	testSingle(0.0f, 0.0f, fov30, hAngle1, vAngle);

	RadianPi fov40(40.0f * DegToRad);
	testSingle(0.0f, 0.0f, fov40, hAngle1, vAngle);

	RadianPi fov60(60.0f * DegToRad);
	testSingle(0.0f, 0.0f, fov60, hAngle1, vAngle);

	RadianPi hAngle2(-30.0f * DegToRad);
	testSingle(0.0f, 0.0f, fov30, hAngle2, vAngle);

	RadianPi hAngle3(30.0f * DegToRad);
	testSingle(0.0f, 0.0f, fov30, hAngle3, vAngle);

	//------------- Two actors test cases ---------------------

	testDouble(-0.5f, 0.0f, +0.5f, 0.0f, fov20, hAngle1, vAngle);

	testDouble(-0.5f, 0.0f, +0.5f, 0.0f, fov30, hAngle1, vAngle);

	testDouble(-0.5f, 0.0f, +0.5f, 0.0f, fov40, hAngle1, vAngle);

	testDouble(-0.5f, 0.0f, +0.5f, 0.0f, fov20, hAngle2, vAngle);

	testDouble(-0.5f, 0.0f, +0.5f, 0.0f, fov20, hAngle3, vAngle);
}