/*
ToricSamples - sample code that provides examples of how to use ToricCam to compute viewpoints and to connect with a rendering engine.

Written in 2015 by Christophe Lino <christophe.lino@inria.fr>

To the extent possible under law, the author(s) have dedicated all copyright and related 
and neighboring rights to this software to the public domain worldwide. This software is 
distributed without any warranty.
You should have received a copy of the CC0 Public Domain Dedication along with this software. 
If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

You may use this sample code for anything you like, it is not covered by the
same license as the ToricCam library.
 */

#ifndef TORIC_SAMPLES_OGRECONNECTION_H
#define TORIC_SAMPLES_OGRECONNECTION_H

#include <toric/Camera.h>
#include <toric/Quaternion.h>
#include <toric/Vector.h>

#include "Ogre.h"

namespace toric
{
	namespace connection
	{
		void FromOgre(Camera &cam, const Ogre::Camera* ogreCam);
		void ToOgre(const Camera &cam, Ogre::Camera* ogreCam);

		/***************************************************************************************************/
		/// \brief	Convert a position in the OGRE y-up system to a position in the Mathematical z-up coordinate system
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		///	\param[in] const Ogre::Vector3 & v	position in OGRE
		///
		/// \return Vector3		position in the mathematical coordinate system
		/***************************************************************************************************/

		inline Vector3 FromOgre(const Ogre::Vector3 &v)
		{
			return Vector3(v[0], -v[2], v[1]);
		}

		/***************************************************************************************************/
		/// \brief	Convert a position in the Mathematical z-up coordinate system to a position in the OGRE y-up system
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		///	\param[in] const Vector3 & v	position in Mathematical z-up coordinate system
		///
		/// \return Vector3		position in the OGRE y-up system
		/***************************************************************************************************/

		inline Ogre::Vector3 ToOgre(const Vector3 &v)
		{
#if OGRE_DOUBLE_PRECISION
			return Ogre::Vector3(v[0], v[2], -v[1]);
#else
			return Ogre::Vector3((float)v[0], (float)v[2], (float)-v[1]);
#endif
		}

		/***************************************************************************************************/
		/// \brief	Convert an orientation in the OGRE y-up system to an orientation in the Mathematical z-up coordinate system
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		///	\param[in] const Ogre::Quaternion & q		orientation in OGRE
		///
		/// \return Vector3		orientation in the mathematical coordinate system
		/***************************************************************************************************/

		inline Quaternion FromOgre( const Ogre::Quaternion & q )
		{
			return Quaternion(q.w, q.x, -q.z, q.y);
		}

		/***************************************************************************************************/
		/// \brief	Convert an orientation in the Mathematical z-up coordinate system to an orientation in the OGRE y-up system
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		///	\param[in] const Quaternion & q		orientation in Mathematical z-up coordinate system
		///
		/// \return Ogre::Quaternion		orientation in the OGRE y-up system
		/***************************************************************************************************/

		inline Ogre::Quaternion ToOgre( const Quaternion & q )
		{
#if OGRE_DOUBLE_PRECISION
			return Ogre::Quaternion(q.s(), q.x(), q.z(), -q.y());
#else
			return Ogre::Quaternion((float)q.s(), (float)q.x(), (float)q.z(), (float)-q.y());
#endif
		}

		/************************************************************************/
		/*                                                                      */
		/************************************************************************/

		inline Vector2 FromOgre(const Ogre::Vector2 &v)
		{
			return Vector2(v[0], -v[1]);
		}

		inline Ogre::Vector2 ToOgre(const Vector2 &v)
		{
#if OGRE_DOUBLE_PRECISION
			return Ogre::Vector2(v.x(), -v.y());
#else
			return Ogre::Vector2((float)v.x(), (float)-v.y());
#endif
		}

		/************************************************************************/
		/*                                                                      */
		/************************************************************************/

		inline RadianPi FromOgre(const Ogre::Radian &r)
		{
			return r.valueRadians();
		}

		inline Ogre::Radian ToOgre(const RadianPi &r)
		{
#if OGRE_DOUBLE_PRECISION
			return Ogre::Radian(r.valueRadians());
#else
			return Ogre::Radian( float(r.valueRadians()) );
#endif
		}

		/***************************************************************************************************/
		/// \brief	Copy all parameters of an OGRE camera into a ToricCam camera
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		///	\param[in,out] Camera & cam					ToricCam camera
		///	\param[in] const Ogre::Camera * ogreCam		OGRE camera
		/***************************************************************************************************/

		inline void FromOgre(Camera &cam, const Ogre::Camera* ogreCam)
		{
			cam.aspect = ogreCam->getAspectRatio();
			cam.setFovY( ogreCam->getFOVy().valueRadians() );
			cam.position = FromOgre( ogreCam->getPosition() );
			cam.orientation = FromOgre( ogreCam->getOrientation() );
		}

		/***************************************************************************************************/
		/// \brief	Copy all parameters of a ToricCam camera into an OGRE camera
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		///	\param[in] const Camera & cam				ToricCam camera
		///	\param[in,out] Ogre::Camera * ogreCam		OGRE camera
		/***************************************************************************************************/

		inline void ToOgre(const Camera &cam, Ogre::Camera* ogreCam)
		{
			ogreCam->setFOVy( Ogre::Radian( cam.getFOVy().valueRadians() ) );
			ogreCam->setAspectRatio( cam.aspect );
			ogreCam->setPosition( ToOgre( cam.position ) );
			ogreCam->setOrientation( ToOgre( cam.orientation ) );
		}
	}
}

#endif