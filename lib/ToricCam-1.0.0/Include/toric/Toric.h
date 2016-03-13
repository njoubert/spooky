/*
 This source file is part of ToricCam (a library for intuitive and efficient virtual camera control)
 For more info on the project, please contact Christophe Lino at christophe.lino@inria.fr
 
 Copyright (c) 2015 Christophe Lino
 Also see acknowledgments in readme.txt
 
 TThis library is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this library.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef TORIC_TORIC_H
#define TORIC_TORIC_H

#include "toric/Euler.h"
#include "toric/Vector.h"
#include "toric/Quaternion.h"

#include <vector>

namespace toric
{
	class Toric2;

	/***************************************************************************************************/
	/// \class	ToricManifold
	///
	/// \brief	The 2d manifold surface representing the solution to an exact on-screen positioning of two targets
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class ToricManifold
	{
	public:
		
		ToricManifold() {}

	private:

		/***************************************************************************************************/
		/// \class	Equation
		///
		/// \brief	The equation of the 2d manifold surface
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		class Equation
		{
			friend ToricManifold;

		private:
			Vector3 m_A;
			Vector3 m_B;
			RadianPi m_alpha;

		public:

			/***************************************************************************************************/
			/// \brief	Constructor
			///
			/// \author	Christophe Lino
			/// \date	2012/07/29
			///
			///	\param[in] Vector3 A		the first target's world position
			///	\param[in] Vector3 B		the second target's world position
			///	\param[in] RadianPi alpha	the angle to satisfy
			/***************************************************************************************************/

			Equation(const Vector3 & A = Vector3(0,0,0), const Vector3 & B = Vector3(0,0,0), const RadianPi & alpha = 0);

			/***************************************************************************************************/
			/// \brief	Get the first target's world position
			///
			/// \author	Christophe Lino
			/// \date	2012/07/29
			///
			/// \return	Vector3		the first target's world position
			/***************************************************************************************************/

			const Vector3 & getA() const;
			
			/***************************************************************************************************/
			/// \brief	Get the second target's world position
			///
			/// \author	Christophe Lino
			/// \date	2012/07/29
			///
			/// \return	Vector3		the second target's world position
			/***************************************************************************************************/

			const Vector3 & getB() const;
			
			/***************************************************************************************************/
			/// \brief	Get the angle to satisfy
			///
			/// \author	Christophe Lino
			/// \date	2012/07/29
			///
			/// \return	Vector3		the angle to satisfy
			/***************************************************************************************************/

			const RadianPi & getAlpha() const;

			/***************************************************************************************************/
			/// \brief	Get the value associated to a world position
			///
			/// \author	Christophe Lino
			/// \date	2012/07/29
			///
			///	\param[in] Vector3 p		the world position to account for
			///
			/// \return double		the value associated to a world position
			/***************************************************************************************************/

			double getValue(const Vector3 & p) const;

			/***************************************************************************************************/
			/// \brief	Get the absolute value (distance) associated to a world position
			///
			/// \author	Christophe Lino
			/// \date	2012/07/29
			///
			///	\param[in] Vector3 p		the world position to account for
			///
			/// \return double		the distance to the world position
			/***************************************************************************************************/

			double getAbsValue(const Vector3 & p) const;
		};

	protected:

		double m_radius;
		Vector3 m_zero;
		Quaternion m_q;
		Equation m_equation;

	public:

		/***************************************************************************************************/
		/// \brief	Creates a manifold surface so that world position wposA projects at pA on the screen, and world position wposB projects at pB on the screen
		///
		///	\param[in]	const RadianPi & fovX			the horizontal field of view of the camera
		///	\param[in]	const double & aspect			the aspect ratio of the camera
		///	\param[in]	const Vector2 & pA				the first target's screen position in [-1;+1]^2
		///	\param[in]	const Vector2 & pB				the second target's screen position in [-1;+1]^2
		///	\param[in]	const Vector3 & wposA			the first target's world position
		///	\param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const Vector3 & zero			(optional) the vector defining phi=0. In the general case, one should not use it.
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/
		
		ToricManifold(const RadianPi & fovX, const double & aspect, const Vector2 & pA, const Vector2 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);

		/***************************************************************************************************/
		/// \brief	Creates a manifold surface so that world position wposA projects at pA on the screen, and world position wposB projects at pB on the screen
		///
		/// \param[in]	const RadianPi & fovX			the horizontal field of view of the camera
		/// \param[in]	const double & aspect			the aspect ratio of the camera
		/// \param[in]	const Vector3 & pA				the first target's screen position in [-1;+1]^2 x R
		/// \param[in]	const Vector3 & pB				the second target's screen position in [-1;+1]^2 x R
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const Vector3 & zero			(optional) the vector defining phi=0. In the general case, one should not use it.
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/
		
		ToricManifold(const RadianPi & fovX, const double & aspect, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);

		/***************************************************************************************************/
		/// \brief	Creates a manifold surface so that world position wposA projects at pA on the screen, and world position wposB projects at pB on the screen
		///
		/// \param[in]	const RadianPi & fovX			the horizontal field of view of the camera
		/// \param[in]	const RadianPi & fovY			the vertical field of view of the camera
		/// \param[in]	const Vector2 & pA				the first target's screen position in [-1;+1]^2
		/// \param[in]	const Vector2& pB				the second target's screen position in [-1;+1]^2
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const Vector3 & zero			(optional) the vector defining phi=0. In the general case, one should not use it.
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/
		
		ToricManifold(const RadianPi & fovX, const RadianPi & fovY, const Vector2 & pA, const Vector2 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);

		/***************************************************************************************************/
		/// \brief	Creates a manifold surface so that world position wposA projects at pA on the screen, and world position wposB projects at pB on the screen
		///
		/// \param[in]	const RadianPi & fovX			the horizontal field of view of the camera
		/// \param[in]	const RadianPi & fovY			the vertical field of view of the camera
		/// \param[in]	const Vector3 & pA				the first target's screen position in [-1;+1]^2 x R
		/// \param[in]	const Vector3 & pB				the second target's screen position in [-1;+1]^2 x R
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const Vector3 & zero			(optional) the vector defining phi=0. In the general case, one should not use it.
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/

		ToricManifold(const RadianPi & fovX, const RadianPi & fovY, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);

		/***************************************************************************************************/
		/// \brief	Creates a manifold surface from an angle to satisfy, and so that world position wposA projects at pA on the screen, and world position wposB projects at pB on the screen
		///
		/// \param[in]	const RadianPi & alpha			the angle to satisfy
		/// \param[out]	const RadianPi & fovX			the horizontal field of view of the camera
		/// \param[in]	const double & aspect			the aspect ratio of the camera
		/// \param[in]	const Vector3 & pA				the first target's screen position in [-1;+1]^2
		/// \param[in]	const Vector3 & pB				the second target's screen position in [-1;+1]^2
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const Vector3 & zero			(optional) the vector defining phi=0. In the general case, one should not use it.
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return ToricManifold	the corresponding manifold surface
		/***************************************************************************************************/

		static ToricManifold BuildFromAlpha(const RadianPi & alpha, RadianPi & fovX, const double & aspect, const Vector2 & pA, const Vector2 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);

	private:
		void create(const double& pSx , const double& pSy, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);
		void create(const RadianPi& fovX, const double & aspect, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);
		void create(const RadianPi& fovX, const RadianPi & fovY, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero=Vector3::ZERO);

	public:
		/***************************************************************************************************/
		/// \brief	Compute a camera position on the manifold surface
		///
		/// \param[in]	const Toric2 & t			the camera position in its toric representation
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Vector3	the corresponding camera position in world coordinates
		/***************************************************************************************************/

		// HACK NJ: This is not implemented anywhere
		// Vector3 computePosition(const Toric2 & t) const;
		
		/***************************************************************************************************/
		/// \brief	Compute a camera position on the manifold surface
		///
		/// \param[in]	const Radian2Pi & theta			the horizontal angle on the manifold, within ]0;2*(pi-getAlpha())[
		/// \param[in]	const RadianPi & phi			the vertical angle on the manifold, within [-pi;+pi]
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Vector3	the corresponding camera position in world coordinates
		/***************************************************************************************************/

		Vector3 computePosition(const Radian2Pi & theta, const RadianPi & phi) const;

		/***************************************************************************************************/
		/// \brief	Compute the camera orientation corresponding to a given position on the manifold surface
		///
		/// \param[in]	const Vector3 & position		the camera position on the manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Quaternion	the corresponding camera orientation
		/***************************************************************************************************/

		Quaternion computeOrientation( const Vector3 & position ) const;

		/***************************************************************************************************/
		/// \brief	Access the angle which generates the manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return const RadianPi &	the angle to satisfy
		/***************************************************************************************************/

		const RadianPi& getAlpha() const;

		/***************************************************************************************************/
		/// \brief	Access the first target's world position
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return const Vector3 &	the first target's world position
		/***************************************************************************************************/

		const Vector3 & getPositionA() const;
		
		/***************************************************************************************************/
		/// \brief	Access the second target's world position
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return const Vector3 &	the second target's world position
		/***************************************************************************************************/

		const Vector3 & getPositionB() const { return m_equation.m_B; }

		/***************************************************************************************************/
		/// \brief	Access the zero vector in world coordinates
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return const Vector3 &	the zero vector in world coordinates
		/***************************************************************************************************/

		const Vector3 & getZero() const { return m_zero; }

		/***************************************************************************************************/
		/// \brief	Access the upper bound (not included) of the allowed interval of values for the horizontal angle
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Radian2Pi	the maximum value for parameter Theta
		/***************************************************************************************************/

		Radian2Pi getMaxTheta() const;

		/***************************************************************************************************/
		/// \brief	Compute the maximum possible distance between one of the targets and a camera position on the manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Radian2Pi	the maximum possible distance
		/***************************************************************************************************/

		double getMaximumDistanceToTargets() const;

		/***************************************************************************************************/
		/// \brief	Compute the distance between a world position and the mandfold surface
		///
		/// \param[in] const Vector3 & point	the world position to consider
		///
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Radian2Pi	the distance to the manifold surface
		/***************************************************************************************************/

		double getDistance(const Vector3 & point) const;

		/***************************************************************************************************/
		/// \brief	Compute the set of solutions to an exact distance constraint to A
		///
		/// \param[in] const double & distance	the distance constraint
		///
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return std::vector<Radian2Pi>	the set of horizontal values for which the constraint is satisfied
		/***************************************************************************************************/

		std::vector<Radian2Pi> getThetasFromDistanceToA(const double & d) const;

		/***************************************************************************************************/
		/// \brief	Compute the set of solutions to an exact distance constraint to B
		///
		/// \param[in] const double & distance	the distance constraint
		///
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return std::vector<Radian2Pi>	the set of horizontal values for which the constraint is satisfied
		/***************************************************************************************************/

		std::vector<Radian2Pi> getThetasFromDistanceToB(const double & d) const;

		/***************************************************************************************************/
		/// \brief	Compute the camera position which satisfies an exact vantage constraint to A
		///
		/// \param[in] const Vector3 & vectorFromA		the vantage angle constraint, as a direction from the first target
		///
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Vector3		the camera position (in toric coordinates) on the manifold surface which the constraint is satisfied
		/***************************************************************************************************/

		Vector3 getPositionFromVantageToA(const Vector3 & vectorFromA) const;

		/***************************************************************************************************/
		/// \brief	Compute the camera position which satisfies an exact vantage constraint to A
		///
		/// \param[in] const Vector3 & vectorFromB		the vantage angle constraint, as a direction from the first target
		///
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Vector3		the camera position (in toric coordinates) on the manifold surface which the constraint is satisfied
		/***************************************************************************************************/

		Vector3 getPositionFromVantageToB(const Vector3 & vectorFromB) const;

		/***************************************************************************************************/
		/// \brief	Compute the camera position which satisfies an exact vantage constraint to the middle point of A and B
		///
		/// \param[in] const Vector3 & vectorFromMiddle		the vantage constraint, as a direction from the middle point of both targets
		///
		///
		/// \author	Christophe Lino
		/// \date	2015/07/26
		///
		/// \return Vector3		the camera position (in toric coordinates) on the manifold surface which the constraint is satisfied
		/***************************************************************************************************/

		Vector3 getPositionFromVantageToMiddleAB(const Vector3 & vectorFromMiddle) const;

		/***************************************************************************************************/
		/// \brief	Compute the horizontal angle which corresponds to a ratio within ]0;1[
		///
		/// \param[in] const double & thetaRatio		the ratio on the horizontal angle (0=second target's world position, 1=first target's world position)
		///
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return Radian2Pi	the horizontal angle on the manifold which corresponds to a the ratio value
		/***************************************************************************************************/

		Radian2Pi getThetaFromRatio(const double & thetaRatio) const;
	};

	/***************************************************************************************************/
	/// \class	Toric2
	///
	/// \brief	2d toric representation of a camera position on a Toric manifold surface
	/// \author	Christophe Lino
	/// \date	2012/07/29
	/***************************************************************************************************/

	class Toric2
	{
	protected:
		/// horizontal angle
		Radian2Pi	m_theta;
		/// vertical angle
		RadianPi	m_phi; 

	public:

		/***************************************************************************************************/
		/// \brief	Copy of the 2d toric representation of a camera position
		///
		/// \param[in]	const Toric2 & t				the position to copy
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/
		Toric2(const Toric2 & t);

		/***************************************************************************************************/
		/// \brief	Create the 2d toric representation of a camera position
		///
		/// \param[in]	const RadianPi2 & theta				the horizontal angle on the manifold surface
		/// \param[in]	const RadianPi & phi				the vertical angle on the manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		/***************************************************************************************************/
		Toric2(const Radian2Pi & theta = 0, const RadianPi & phi = 0);
		
		/***************************************************************************************************/
		/// \brief	Access the horizontal angle
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return	const RadianPi2 &		the horizontal angle on the manifold surface
		/***************************************************************************************************/
		const Radian2Pi   & getTheta() const;
		
		/***************************************************************************************************/
		/// \brief	Access the vertical angle
		///
		/// \author	Christophe Lino
		/// \date	2012/07/29
		///
		/// \return	const RadianPi &		the vertical angle on the manifold surface
		/***************************************************************************************************/
		const RadianPi    & getPhi()   const;
	};

	/***************************************************************************************************/
	/// \class	Toric3
	///
	/// \brief	3d toric representation of a camera position on a manifold surface
	/// \author	Christophe Lino
	/// \date	2013/10/03
	/***************************************************************************************************/

	class Toric3 : public Toric2
	{
	private:
		/// the generator angle (angle to satisfy for a given pair of screen positions)
		RadianPi	m_alpha;
		
	public:

		/***************************************************************************************************/
		/// \brief	Copy of the 3d toric representation of a camera position
		///
		/// \param[in]	const Toric3 & t				the position to copy
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		/***************************************************************************************************/

		Toric3(const Toric3 & t);

		/***************************************************************************************************/
		/// \brief	Create the 2d toric representation of a camera position
		///
		/// \param[in]	const RadianPi & alpha				the angle which generates the manifold surface
		/// \param[in]	const RadianPi2 & theta				the horizontal angle on the manifold surface. Should be whithin ]0;2*(pi-alpha)[
		/// \param[in]	const RadianPi & phi				the vertical angle on the manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		/***************************************************************************************************/

		Toric3(const RadianPi & alpha = 0, const Radian2Pi & theta = 0, const RadianPi & phi = 0);

		/***************************************************************************************************/
		/// \brief	Access the generator angle
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	const RadianPi &		the angle which generates the manifold surface
		/***************************************************************************************************/

		const RadianPi & getAlpha() const;

		/***************************************************************************************************/
		/// \brief	Change the horizontal angle
		///
		/// \param[in]	const RadianPi2 & theta		the new horizontal angle on the manifold surface
		/// 
		/// \author	Christophe Lino
		/// \date	2013/10/03
		/***************************************************************************************************/

		void setTheta(const Radian2Pi & theta);

		/***************************************************************************************************/
		/// \brief	Change the vertical angle
		///
		/// \param[in]	const RadianPi & phi		the new vertical angle on the manifold surface
		/// 
		/// \author	Christophe Lino
		/// \date	2013/10/03
		/***************************************************************************************************/

		void setPhi  (const RadianPi  & phi);

		/***************************************************************************************************/
		/// \brief	Change the generator angle
		///
		/// \param[in]	const RadianPi & alpha		the generator angle of the new manifold surface
		/// 
		/// \author	Christophe Lino
		/// \date	2013/10/03
		/***************************************************************************************************/

		void setAlpha(const RadianPi  & alpha);

		/***************************************************************************************************/
		/// \brief	Access the ratio on the horizontal angle, in ]0;1[
		/// 
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	double		the ratio on the horizontal angle
		/***************************************************************************************************/

		double getThetaRatio() const;

		/***************************************************************************************************/
		/// \brief	Change all the angles
		///
		/// \param[in]	const RadianPi & alpha				the angle which generates the manifold surface
		/// \param[in]	const RadianPi2 & theta				the horizontal angle on the manifold surface
		/// \param[in]	const RadianPi & phi				the vertical angle on the manifold surface
		/// 
		/// \author	Christophe Lino
		/// \date	2013/10/03
		/***************************************************************************************************/

		void set(const RadianPi  & alpha, const Radian2Pi & theta, const RadianPi  & phi);

		bool operator==(const Toric3 & t) const;
		bool operator!=(const Toric3 & t) const;

		/***************************************************************************************************/
		/// \brief	Compute the Toric representation of a camera position expressed in its Cartesian representation
		///
		/// \param[in]	const Vector3 & wpos			the camera's world position (Cartesian)
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const Vector3 & zero			(optional) the vector defining phi=0. In the general case, one should not use it.
		/// 
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return Toric3		the Toric representation of the input Cartesian position w.r.t the pair of input targets' positions
		/***************************************************************************************************/

		static Toric3  FromWorldPosition(const Vector3 & wpos, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero = Vector3(0,0,0));

		/***************************************************************************************************/
		/// \brief	Compute the Cartesian representation of a camera position expressed in its Toric representation
		///
		/// \param[in]	const Toric3 & tposP			the camera's world position (Cartesian)
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const Vector3 & zero			(optional) the vector defining phi=0. In the general case, one should not use it.
		/// 
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return Toric3		the Cartesian representation of the Toric position w.r.t the pair of input targets' positions
		/***************************************************************************************************/

		static Vector3 ToWorldPosition  (const Toric3  & tpos, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero = Vector3(0,0,0));

		/***************************************************************************************************/
		/// \brief	Compute a ratio of horizontal angle, in ]0;1[, from its value in radians on a given ToricManifold surface
		/// 
		/// \param[in]	const RadianPi2 & theta				the horizontal angle on the manifold surface
		/// \param[in]	const RadianPi & alpha				the angle which generates the manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	double		the ratio of horizontal angle
		/***************************************************************************************************/

		static double    ComputeThetaRatio(const Radian2Pi & theta,		 const RadianPi & alpha);
		
		/***************************************************************************************************/
		/// \brief	Compute an horizontal angle in radians from its ratio value, in ]0;1[, on a given manifold surface
		/// 
		/// \param[in]	const double & thetaRatio			the horizontal angle ratio on the manifold surface
		/// \param[in]	const RadianPi & alpha				the angle which generates the manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	RadianPi2		the horizontal angle
		/***************************************************************************************************/

		static Radian2Pi ComputeTheta     (const double    & thetaRatio, const RadianPi & alpha);

		/***************************************************************************************************/
		/// \brief	Scales an input Toric position by using a new generator angle
		/// 
		/// \param[in]	const Toric3 & reference			the initial Toric position
		/// \param[in]	const RadianPi & alpha				the angle which generates the new manifold surface
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	Toric3	The new scaled Toric position
		/***************************************************************************************************/

		static Toric3	Scale(const Toric3 & reference, const RadianPi & new_alpha);

		/***************************************************************************************************/
		/// \brief	Compute the camera orientation which, from a position, forces a single target to project at a given screen position
		/// 
		/// \param[in]	const Vector3 & campos			the camera's world position
		/// \param[in]	const Vector2 & spos			the target's screen position
		/// \param[in]	const Vector3 & wpos			the target's world position
		/// \param[in]	const RadianPi & fovX			the camera's horizontal field of view angle
		/// \param[in]	const RadianPi & fovY			the camera's vertical field of view angle
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	Quaternion		the camera orientation
		/***************************************************************************************************/

		static Quaternion ComputeOrientationForOneTarget(const Vector3 & campos, const Vector2 & spos, const Vector3 & wpos, const RadianPi & fovX, const RadianPi & fovY);

		/***************************************************************************************************/
		/// \brief	Compute the camera orientation which, from a position, forces two targets to project at two given screen positions
		/// 
		/// \param[in]	const Vector3 & campos			the camera's world position
		/// \param[in]	const Vector2 & sposA			the first target's screen position
		/// \param[in]	const Vector2 & sposB			the second target's screen position
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const RadianPi & fovX			the camera's horizontal field of view angle
		/// \param[in]	const RadianPi & fovY			the camera's vertical field of view angle
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	Quaternion		the camera orientation
		/***************************************************************************************************/
		
		static Quaternion ComputeOrientationForTwoTargets(const Vector3 & campos, const Vector2 & sposA, const Vector2 & sposB, const Vector3 & wposA, const Vector3 & wposB, const RadianPi & fovX, const RadianPi & fovY);
		
		/***************************************************************************************************/
		/// \brief	Compute the camera orientation which, from a position, frames two targets at two given screen positions, with a roll angle equal to 0. NB: it does not strictly enforces the screen positions.
		/// 
		/// \param[in]	const Vector3 & campos			the camera's world position
		/// \param[in]	const Vector2 & sposA			the first target's screen position
		/// \param[in]	const Vector2 & sposB			the second target's screen position
		/// \param[in]	const Vector3 & wposA			the first target's world position
		/// \param[in]	const Vector3 & wposB			the second target's world position
		/// \param[in]	const RadianPi & fovX			the camera's horizontal field of view angle
		/// \param[in]	const RadianPi & fovY			the camera's vertical field of view angle
		///
		/// \author	Christophe Lino
		/// \date	2013/10/03
		///
		/// \return	Quaternion		the camera (free from roll) orientation
		/***************************************************************************************************/
		
		//static Quaternion ComputeOrientationForTwoTargetsWithNoRoll( const Vector3 & campos, const Vector2 & sposA, const Vector2 & sposB, const Vector3 & wposA, const Vector3 & wposB, const RadianPi & fovX, const RadianPi & fovY );
		
		/// You should not use the following function except if you know what you are doing !
		RadianPi _getBeta() const;

		/// You should not use the following function except if you know what you are doing !
		static Quaternion _ComputeOrientationForOneTarget( const Vector3 & campos, const Vector2 & spos, const Vector3 & wpos, const double & Sx, const double & Sy );
		/// You should not use the following function except if you know what you are doing !
		static Quaternion _ComputeOrientationForTwoTargets( const Vector3 & campos, const Vector2 & sposA, const Vector2 & sposB, const Vector3 & wposA, const Vector3 & wposB, const double & Sx, const double & Sy );
		/// You should not use the following function except if you know what you are doing !
		//static Quaternion _ComputeOrientationForTwoTargetsWithNoRoll( const Vector3 & campos, const Vector2 & sposA, const Vector2 & sposB, const Vector3 & wposA, const Vector3 & wposB, const double & Sx, const double & Sy );

		/// You should not use the following function except if you know what you are doing !
		static Quaternion _ComputeOrientationForOneTarget( const Vector3 & campos, const Vector3 & spos, const Vector3 & wpos, const double & Sx, const double & Sy );
		/// You should not use the following function except if you know what you are doing !
		static Quaternion _ComputeOrientationForTwoTargets( const Vector3 & campos, const Vector3 & sposA, const Vector3 & sposB, const Vector3 & wposA, const Vector3 & wposB, const double & Sx, const double & Sy );
		/// You should not use the following function except if you know what you are doing !
		//static Quaternion _ComputeOrientationForTwoTargetsWithNoRoll( const Vector3 & campos, const Vector3 & sposA, const Vector3 & sposB, const Vector3 & wposA, const Vector3 & wposB, const double & Sx, const double & Sy );
	};
}

#endif