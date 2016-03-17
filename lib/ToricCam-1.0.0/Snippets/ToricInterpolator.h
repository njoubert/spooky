/*
 This source file is part of ToricCam (a library for intuitive and efficient virtual camera control)
 For more info on the project, please contact Christophe Lino at christophe.lino@inria.fr
 
 Copyright (c) 2015 Christophe Lino
 Also see acknowledgments in readme.txt
 
 TThis library is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 ToricCam is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this library.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef TORIC_INTERPOLATOR_H
#define TORIC_INTERPOLATOR_H

#include "toric/Toric.h"
#include "toric/Vector.h"
#include "toric/Euler.h"

namespace toric
{	
	/// \struct ToricInterpolationInfo
	/// represent the information needed to interpolate two viewpoints
	struct ToricInterpolationInfo
	{
		Vector3 startVector;
		RadianPi viewAngleChange;
		RadianPi viewHeightChange;
		double distance[2];
	};

	/// \class ToricInterpolator
	/// allowed interpolating two positions expressed in the same reference Toric Space
	class ToricInterpolator
	{
	private:
		ToricInterpolationInfo m_infoA, m_infoB;
		double m_alpha[2];
		Vector3 m_wposA, m_wposB;

	public:
		ToricInterpolator() {}

		ToricInterpolator(const Vector3 & wposA, const Vector3 & wposB, const Toric3 & t1, const Toric3 & t2)
		{
			init(wposA, wposB, t1, t2);
		}

		void init(const Vector3 & wposA, const Vector3 & wposB, const Toric3 & t1, const Toric3 & t2);

		void interpolateVector(const double & t, Vector3 & pOutVecA, Vector3 & pOutVecB);

		Toric3 interpolate(const double & t);
	};
}

#endif