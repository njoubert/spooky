/*
 This source file is part of ToricCam (a library for intuitive and efficient virtual camera control)
 For more info on the project, please contact Christophe Lino at christophe.lino@inria.fr
 
 Copyright (c) 2015 Christophe Lino
 Also see acknowledgments in readme.txt
 
 ToricCam is free software: you can redistribute it and/or modify
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

#include "toric/ToricInterpolator.h"
#include "toric/Plane.h"

namespace toric
{
	/************************************************************************/
	/* ToricInterpolator                                                    */
	/************************************************************************/

	double EaseInOut(double x)	{ return ( sin( ( (x)-0.5 ) * PI ) + 1 ) * 0.5; }

	void ToricInterpolator::init( const Vector3 & wposA, const Vector3 & wposB, const Toric3 & t1, const Toric3 & t2 )
	{
		m_wposA = wposA;
		m_wposB = wposB;
		m_alpha[0] = t1.getAlpha().valueRadians();
		m_alpha[1] = t2.getAlpha().valueRadians();

		Plane
			viewPlaneA = Plane::createPlaneFromNormal(Vector3::UNIT_Z, wposA),
			viewPlaneB = Plane::createPlaneFromNormal(Vector3::UNIT_Z, wposB);

		Vector3
			p1 = Toric3::ToWorldPosition(t1, wposA, wposB),
			p2 = Toric3::ToWorldPosition(t2, wposA, wposB);

		{ // A
			Vector3
				y1 = p1 - wposA, 
				y2 = p2 - wposA;
			double
				d1 = y1.norm(),
				d2 = y2.norm();
			y1.normalize();
			y2.normalize();
			m_infoA.startVector = y1;
			Vector3 
				y1Proj = viewPlaneA.getProjection(p1)-wposA, 
				y2Proj = viewPlaneA.getProjection(p2)-wposA;
			y1Proj.normalize();
			y2Proj.normalize();
			m_infoA.viewAngleChange = y1Proj.directedAngle(y2Proj, Vector3::UNIT_Z);
			m_infoA.viewHeightChange = (Vector3::UNIT_Z.angle(y1) - Vector3::UNIT_Z.angle(y1Proj)) - (Vector3::UNIT_Z.angle(y2)-Vector3::UNIT_Z.angle(y2Proj));
			m_infoA.distance[0] = d1;
			m_infoA.distance[1] = d2;
		}
		{ // B
			Vector3
				y1 = p1 - wposB, 
				y2 = p2 - wposB;
			double
				d1 = y1.norm(),
				d2 = y2.norm();
			y1.normalize();
			y2.normalize();
			m_infoB.startVector = y1;
			Vector3
				y1Proj = viewPlaneB.getProjection(p1)-wposB,
				y2Proj = viewPlaneB.getProjection(p2)-wposB;
			y1Proj.normalize();
			y2Proj.normalize();
			m_infoB.viewAngleChange = y1Proj.directedAngle(y2Proj, Vector3::UNIT_Z);
			m_infoB.viewHeightChange = (Vector3::UNIT_Z.angle(y1) - Vector3::UNIT_Z.angle(y1Proj)) - (Vector3::UNIT_Z.angle(y2)-Vector3::UNIT_Z.angle(y2Proj));
			m_infoB.distance[0] = d1;
			m_infoB.distance[1] = d2;
		}
	}
	
	void ToricInterpolator::interpolateVector( const double & t, Vector3 & pOutVecA, Vector3 & pOutVecB )
	{
		{
			pOutVecA = Quaternion(Vector3::UNIT_Z, m_infoA.viewAngleChange * t) * m_infoA.startVector;
			pOutVecA = Quaternion(pOutVecA ^ Vector3::UNIT_Z, m_infoA.viewHeightChange * t) * pOutVecA;
		}
		{
			pOutVecB = Quaternion(Vector3::UNIT_Z, m_infoB.viewAngleChange * t) * m_infoB.startVector;
			pOutVecB = Quaternion(pOutVecB ^ Vector3::UNIT_Z, m_infoB.viewHeightChange * t) * pOutVecB;
		}
		Vector3 vecAB = m_wposB-m_wposA;
		double AB = vecAB.norm();
		double alpha = m_alpha[0] * (1-t) + m_alpha[1] * t;
		double PiMinusAlpha = PI-alpha;
		double transform = PI / PiMinusAlpha;
		double dA;
		{
			double dA1 = m_infoA.distance[0] * (1-t) + m_infoA.distance[1] * t;
			double beta = pOutVecA.angle(vecAB).valueRadians();
			beta = clamp(beta, 0.0, PiMinusAlpha);
			double dA2 = ComputeDistanceToA(AB, alpha, beta*2);
			double wA2 = EaseInOut( sin( beta * transform ) );
			dA = (dA1 + dA2 * wA2) / (1 + wA2);
		}
		double dB;
		{
			double dB1 = m_infoB.distance[0] * (1-t) + m_infoB.distance[1] * t;
			double beta = pOutVecB.angle(-vecAB).valueRadians();
			beta = clamp(beta, 0.0, PiMinusAlpha);
			double dB2 = ComputeDistanceToA(AB, alpha, beta*2);
			double wB2 = EaseInOut( sin( beta * transform ) );
			dB = (dB1 + dB2 * wB2) / (1 + wB2);
		}
		pOutVecA = pOutVecA * dA;
		pOutVecB = pOutVecB * dB;
	}

	Toric3 ToricInterpolator::interpolate( const double & t )
	{
		Vector3 vecA, vecB; interpolateVector(t, vecA, vecB);

		Vector3 p = ( (m_wposA+vecA) + (m_wposB+vecB) ) * 0.5;

		Toric3 res = Toric3::FromWorldPosition(p, m_wposA, m_wposB);

		return res;
	}
}