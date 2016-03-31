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

#include "toric/Toric.h"
#include "toric/ProjectionMatrix.h"

#include <assert.h>
#include <iostream>

namespace toric
{
	void ToricManifold::create(const double& pSx , const double& pSy, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero)
	{
		Vector3 pA3 = ProjectionMatrix::GetVectorInCameraSpace(pA, pSx, pSy);
		Vector3 pB3 = ProjectionMatrix::GetVectorInCameraSpace(pB, pSx, pSy);
		RadianPi alpha = pB3.angle(pA3);

		const Vector3
			& A = wposA,
			& B = wposB;

		m_equation = Equation(A, B, alpha);

		Vector3 vecAB = B-A;
		Vector3 n = -vecAB;
		if(zero.norm())
		{
			m_zero = zero;
		}
		else
		{
			Vector2 n2 = n.projectZ();
			n2.rotate90();
			m_zero = Vector3(n2.x(),n2.y(),0);
		}

		double AB = n.norm();
		Vector3 AB_middle = (A+B)/2;

		double t = AB / (2 * tan(alpha));
		m_radius = AB / (2 * sin(alpha));

		Vector3 right, forward, up(0,0,1);
		{
			pA3.normalize(); pB3.normalize();

			up = pB3 ^ pA3;			up.normalize();
			forward = pA3 + pB3;	forward.normalize();
			right = forward ^ up;	right.normalize();
		}

		m_q = Quaternion(right,forward,up);
	}

	void ToricManifold::create( const RadianPi & fovX, const double & aspect, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		double Sx, Sy;
		ProjectionMatrix::ComputeScale(fovX, aspect, Sx, Sy);
		create(Sx, Sy, pA, pB, wposA, wposB, zero);
	}

	void ToricManifold::create( const RadianPi & fovX, const RadianPi & fovY, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		double Sx, Sy;
		ProjectionMatrix::ComputeScale(fovX, fovY, Sx, Sy);
		create(Sx, Sy, pA, pB, wposA, wposB, zero);
	}

	ToricManifold::ToricManifold( const RadianPi & fovX, const double & aspect, const Vector2 & pA, const Vector2 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		Vector3 pA3d(pA.x(),pA.y(),1), pB3d(pB.x(),pB.y(),1);
		create(fovX, aspect, pA3d, pB3d, wposA, wposB, zero);
	}

	ToricManifold::ToricManifold(const RadianPi & fovX, const RadianPi & fovY, const Vector2 & pA, const Vector2 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		Vector3 pA3d(pA.x(),pA.y(),1), pB3d(pB.x(),pB.y(),1);
		create(fovX, fovY, pA3d, pB3d, wposA, wposB, zero);
	}

	ToricManifold::ToricManifold( const RadianPi & fovX, const double & aspect, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		create(fovX, aspect, pA, pB, wposA, wposB, zero);
	}

	ToricManifold::ToricManifold(const RadianPi & fovX, const RadianPi & fovY, const Vector3 & pA, const Vector3 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		create(fovX, fovY, pA, pB, wposA, wposB, zero);
	}

	ToricManifold ToricManifold::BuildFromAlpha( const RadianPi & alpha, RadianPi & fovX, const double & aspect, const Vector2 & pA, const Vector2 & pB, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		Vector3 pA3;
		Vector3 pB3;

		double fmin=0, fmax = PI;
		double angle;
		do
		{
			double
				fovX = (fmax+fmin)/2,
				fovY = fovX/aspect,
				tanx = tan(fovX/2),
				tany = tan(fovY/2);
			double Sx = 1. / tanx;
			double Sy = 1. / tany;

			pA3 = Vector3(pA[0]/Sx, 1, pA[1]/Sy);
			pB3 = Vector3(pB[0]/Sx, 1, pB[1]/Sy);
			angle = pB3.angle(pA3).valueRadians();

			if( angle < alpha.valueRadians() )
				fmin = fovX;
			else
				fmax = fovX;

		} while( fabs(alpha.valueRadians() - angle) > 1e-10 );

		fovX = (fmax+fmin)/2;

		return ToricManifold(fovX, aspect, pA, pB, wposA, wposB, zero);
	}

	Vector3 ToricManifold::computePosition( const Radian2Pi & theta, const RadianPi & phi ) const
	{
		Toric3 t(getAlpha(), theta, phi);
		return Toric3::ToWorldPosition(t, getPositionA(), getPositionB(), m_zero);
	}

	std::vector<Radian2Pi> ToricManifold::getThetasFromDistanceToB( const double & d ) const
	{
		std::vector<Radian2Pi> v;

		double alpha = getAlpha().valueRadians();

		double AB = m_radius * (2 * sin(alpha));
		double radius2 = 2 * m_radius;
		double beta = acos(d/radius2);

		if( d == radius2 )
		{
			Radian2Pi theta = PI;
			v.push_back( theta );
		}
		else if( 0 < d && d <= AB )		
		{
			Radian2Pi theta = (PI - 2 * beta );
			v.push_back( theta );
		}
		else if( AB < d && d < radius2 )
		{
			Radian2Pi theta1 = (PI - 2 * beta );
			Radian2Pi theta2 = (PI + 2 * beta );
			v.push_back( theta1 );
			v.push_back( theta2 );
		}

		return v;
	}

	std::vector<Radian2Pi> ToricManifold::getThetasFromDistanceToA( const double & d ) const
	{
		std::vector<Radian2Pi> v;

		double alpha = getAlpha().valueRadians();

		double AB = m_radius * (2 * sin(alpha));
		double radius2 = 2 * m_radius;
		double beta = acos(d/radius2);

		if( d == radius2 )
		{
			Radian2Pi theta = PI - 2 * alpha;
			v.push_back( theta );
		}
		else if( 0 < d && d <= AB )	
		{
			Radian2Pi theta = PI - 2 * (alpha-beta);
			v.push_back( theta );
		}
		else if( AB < d && d < radius2 )
		{
			Radian2Pi theta1 = PI - 2 * (alpha-beta);
			Radian2Pi theta2 = PI - 2 * (alpha+beta);
			v.push_back( theta1 );
			v.push_back( theta2 );
		}

		return v;
	}

	double ToricManifold::getDistance( const Vector3 & point ) const
	{
		return m_equation.getAbsValue(point);
	}

	Vector3 ToricManifold::getPositionFromVantageToA( const Vector3 & direction ) const
	{
		const Vector3 
			& wposA = m_equation.getA(), 
			& wposB = m_equation.getB();
		Vector3 AB = wposB-wposA;

		RadianPi beta = AB.angle(direction);
		double d = AB.norm() * sin(PI-getAlpha().valueRadians()-beta.valueRadians()) / sin(getAlpha());
		
		Vector3 v = direction; v.normalize();
		
		return wposA + v * d;
	}

	Vector3 ToricManifold::getPositionFromVantageToB( const Vector3 & direction ) const
	{
		const Vector3 
			& wposA = m_equation.getA(), 
			& wposB = m_equation.getB();
		
		Vector3 BA = wposA-wposB;
		
		RadianPi beta_p = BA.angle(direction);
		double d = BA.norm() * sin(PI-getAlpha().valueRadians()-beta_p.valueRadians()) / sin(getAlpha());
		
		Vector3 v = direction; v.normalize();
		
		return wposB + v * d;
	}

	Vector3 ToricManifold::getPositionFromVantageToMiddleAB( const Vector3 & direction ) const
	{
		const Vector3 
			& wposA = m_equation.getA(), 
			& wposB = m_equation.getB();
		const double & alpha = getAlpha().valueRadians();
		Vector3 I = (wposA+wposB) / 2.0;
		Vector3 vec = direction.normalized();

		Toric3 tVec = Toric3::FromWorldPosition(I+direction, wposA, wposB, m_zero);

		Toric3 tO(2*alpha, PI-2*alpha, tVec.getPhi());
		double t =  m_radius * cos(alpha);
		Quaternion qP((wposA-wposB).normalized(), tVec.getPhi());
		Vector3 O = I + qP * m_zero * t;

		Vector3 vecIO = O-I;
		RadianPi angle = vec.angle(vecIO);

		double l1 = m_radius * cos(alpha) * cos(angle);
		double dperp  =  m_radius * cos(alpha) * sin(angle);
		double l2 = sqrt( m_radius*m_radius - dperp*dperp );
		
		double l = l1+l2;
		double s = vec.norm();
		
		return I + vec * l;
	}
	
	Quaternion ToricManifold::computeOrientation( const Vector3 & position ) const
	{
		const Vector3 dA(m_equation.getA()-position);
		const Vector3 dB(m_equation.getB()-position);
		Vector3 right, forward, up(0,0,1);
		{
			up = dB.crossProduct(dA);
			up.normalize();

			forward = dA.normalized() + dB.normalized();
			forward.normalize();

			right = forward.crossProduct(up); right.normalize();
		}

		Quaternion q(right,forward,up);

		return q * m_q.inverse();
	}

	Radian2Pi ToricManifold::getThetaFromRatio( const double & thetaRatio ) const
	{
		return Toric3::ComputeTheta(thetaRatio, getAlpha());
	}

	double ToricManifold::getMaximumDistanceToTargets() const
	{
		return m_radius / sin(getAlpha().valueRadians());
	}

	toric::Radian2Pi ToricManifold::getMaxTheta() const
	{
		return 2*(PI-getAlpha().valueRadians());
	}

	const RadianPi& ToricManifold::getAlpha() const
	{
		return m_equation.m_alpha;
	}

	const Vector3 & ToricManifold::getPositionA() const
	{
		return m_equation.m_A;
	}

	/************************************************************************/
	/* ToricManifold Equation                                               */
	/************************************************************************/

	ToricManifold::Equation::Equation( const Vector3 & A, const Vector3 & B, const RadianPi & alpha )
		: m_A(A), m_B(B), m_alpha(alpha)
	{
			
	}

	double ToricManifold::Equation::getValue( const Vector3 & p ) const
	{
		Vector3 PA = (m_A-p), PB = (m_B-p);
		return ( PB.angle(PA).valueRadians() - m_alpha.valueRadians() );
	}

	double ToricManifold::Equation::getAbsValue( const Vector3 & p ) const
	{
		return fabs( getValue(p) );
	}

	const Vector3 & ToricManifold::Equation::getA() const
	{
		return m_A;
	}

	const Vector3 & ToricManifold::Equation::getB() const
	{
		return m_B;
	}

	const RadianPi & ToricManifold::Equation::getAlpha() const
	{
		return m_alpha;
	}

	/************************************************************************/
	/* Toric2                                                               */
	/************************************************************************/

	Toric2::Toric2(const Toric2 & t) 
		: m_theta(t.getTheta()), m_phi(t.getPhi())
	{

	}

	Toric2::Toric2(const Radian2Pi & theta, const RadianPi & phi) 
		: m_theta(theta), m_phi(phi)
	{

	}

	const Radian2Pi   & Toric2::getTheta() const
	{
		return m_theta;
	}

	const RadianPi    & Toric2::getPhi() const
	{
		return m_phi;
	}

	/************************************************************************/
	/* Toric3                                                               */
	/************************************************************************/

	RadianPi ComputeAlpha( const double & AB, const RadianPi & beta, const double & d )
	{
		double num = d - AB * cos(beta);
		double den = sqrt( d*d + AB*AB - 2 * d * AB * cos(beta) );

		double val = clamp(num / den, -1., +1.);
		RadianPi alpha = acos( val );

		return alpha;
	}

	Toric3::Toric3(const Toric3 & t) 
		: Toric2(t.getTheta(), t.getPhi()), m_alpha(t.getAlpha())
	{

	}

	Toric3::Toric3(const RadianPi & alpha, const Radian2Pi & theta, const RadianPi & phi)
		: Toric2(theta, phi), m_alpha(alpha)
	{
		m_alpha = clamp(m_alpha.valueRadians(), 1e-3, PI-1e-3);
		m_theta = clamp(m_theta.valueRadians(), 1e-3, 2*(PI-getAlpha().valueRadians())-1e-3);
	}

	double Toric3::getThetaRatio() const { return ComputeThetaRatio( getTheta(), getAlpha() ); }

	Toric3 Toric3::FromWorldPosition( const Vector3 & wposP, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero)
	{
		Vector3 AB(wposB-wposA);
		Vector3 AP(wposP-wposA);

		Vector3 n = AP.crossProduct(AB); n.normalize();
		Vector3 z;
		if(zero.norm())
		{
			z = zero;
		}
		else
		{
			Vector2 n2 = AB.projectZ();
			n2.rotate270();
			z = Vector3(n2.x(),n2.y(),0); z.normalize();
		}

		RadianPi beta = AB.angle(AP);
		RadianPi alpha = ComputeAlpha(AB.norm(), beta, AP.norm());
		Radian2Pi theta = beta.valueRadians() * 2;
		RadianPi phi = z.directedAngle(n, -AB).valueRadians() - PI/2;
			
		Toric3 res(alpha, theta, phi);

		return res;
	}

	Vector3 Toric3::ToWorldPosition( const Toric3 & t3, const Vector3 & wposA, const Vector3 & wposB, const Vector3 & zero )
	{
		Vector3 vecAB = wposB-wposA;
		double AB = vecAB.norm();

		Vector3 n = -vecAB; n.normalize();
		Vector3 z;
		if(zero.norm())
		{
			z = zero;
		}
		else
		{
			Vector2 n2 = n.projectZ();
			n2.rotate90();
			z = Vector3(n2.x(),n2.y(),0); z.normalize();
		}

		Quaternion qP(n, t3.getPhi());
		RadianPi beta = t3.getTheta().valueRadians() / 2;

		Vector3 t = z.crossProduct(n);
			
		Quaternion qT(t, beta);
		double d = ComputeDistanceToA(AB, t3.getAlpha(), t3.getTheta());

		Vector3 res = qP * qT * vecAB;
		res = res * d / AB + wposA;

		return res;
	}

	double Toric3::ComputeThetaRatio( const Radian2Pi & theta, const RadianPi & alpha )
	{
	#ifdef _DEBUG
		assert( theta.valueRadians() < 2 * (PI-alpha.valueRadians()) );
	#endif
		return theta.valueRadians() / ( 2 * (PI-alpha.valueRadians()) );
	}

	Radian2Pi Toric3::ComputeTheta( const double & theta_r, const RadianPi & alpha )
	{
	#ifdef _DEBUG
		assert( 0 < theta_r && theta_r < 1 );
	#endif
		return theta_r * ( 2 * (PI-alpha.valueRadians()) );
	}

	bool Toric3::operator==( const Toric3 & t ) const
	{
		return t.getAlpha().valueRadians() == getAlpha().valueRadians()
			&& t.getTheta().valueRadians() == getTheta().valueRadians() 
			&& t.getPhi().valueRadians() == getPhi().valueRadians();
	}

	bool Toric3::operator!=( const Toric3 & t ) const
	{
		return !operator==(t);
	}

	void Toric3::setAlpha( const RadianPi & alpha )
	{
	#ifdef _DEBUG
		assert( 0 < alpha.valueRadians() && alpha.valueRadians() < PI );
	#endif
		m_alpha  = alpha;
	}

	void Toric3::setTheta( const Radian2Pi & theta )
	{
#ifdef _DEBUG
		assert( theta.valueRadians() < 2 * (PI-getAlpha().valueRadians()));
#endif
		m_theta = theta;
	}

	void Toric3::setPhi( const RadianPi & phi )
	{
		m_phi  = phi;
	}

	void Toric3::set( const RadianPi & alpha, const Radian2Pi & theta, const RadianPi & phi )
	{
	#ifdef _DEBUG
		assert( 0 < alpha.valueRadians() && alpha.valueRadians() < PI );
		assert( theta.valueRadians() < 2 * (PI-alpha.valueRadians()) );
	#endif
		m_alpha  = alpha;
		m_theta = theta;
		m_phi  = phi;
	}

	Quaternion Toric3::ComputeOrientationForOneTarget( const Vector3 & campos, const Vector2 & spos, const Vector3 & wpos, const RadianPi & fovX, const RadianPi & fovY )
	{
		double Sx, Sy;
		ProjectionMatrix::ComputeScale(fovX, fovY, Sx, Sy);
		return _ComputeOrientationForOneTarget(campos, spos, wpos, Sx, Sy);
	}

	Quaternion Toric3::ComputeOrientationForTwoTargets( const Vector3 & campos, const Vector2 & sposA, const Vector2 & sposB, const Vector3 & wposA, const Vector3 & wposB, const RadianPi & fovX, const RadianPi & fovY )
	{
		double Sx, Sy;
		ProjectionMatrix::ComputeScale(fovX, fovY, Sx, Sy);
		return _ComputeOrientationForTwoTargets(campos, sposA, sposB, wposA, wposB, Sx, Sy);
	}

	Quaternion Toric3::_ComputeOrientationForOneTarget( const Vector3 & campos, const Vector3 & spos, const Vector3 & wpos, const double & Sx, const double & Sy )
	{
		Vector3 r(0,0,0), f(0,0,0), u(0,0,1);
		{ 
			f = wpos - campos;	f.normalize();
			r = f.crossProduct(u);			r.normalize();
			u = r.crossProduct(f);			u.normalize();
		}
		Quaternion q_ref(r, f, u);

		Vector3 right(0,0,0), forward(0,0,0), up(0,0,1);
		{ 
			Vector3 pA3 = ProjectionMatrix::GetVectorInCameraSpace(spos, Sx, Sy);
			pA3.normalize();

			forward = pA3;			
			right = forward.crossProduct(up);	right.normalize();
			up = right.crossProduct(forward);	up.normalize(); 
		}

		Quaternion q_compo(right,forward,up);

		return q_ref * q_compo.inverse();
	}

	Quaternion Toric3::_ComputeOrientationForOneTarget( const Vector3 & campos, const Vector2 & spos, const Vector3 & wpos, const double & Sx, const double & Sy )
	{
		Vector3 spos3(spos.x(), spos.y(), 1);
		return _ComputeOrientationForOneTarget(campos, spos3, wpos, Sx, Sy);
	}

	Quaternion Toric3::_ComputeOrientationForTwoTargets( const Vector3 & campos, const Vector3 & sposA, const Vector3 & sposB, const Vector3 & wposA, const Vector3 & wposB, const double & Sx, const double & Sy )
	{
		Vector3 r(0,0,0), f(0,0,0), u(0,0,1);
		{
			Vector3 dA(wposA - campos), dB(wposB - campos);
			dA.normalize(); dB.normalize();
			u = dB.crossProduct(dA);	u.normalize();
			f = dA + dB;	f.normalize();
			r = f.crossProduct(u);		r.normalize();
			std::cout<<"a: "<<dA[0]<<","<<dA[1]<<","<<dA[2]<<" b: "<<dB[0]<<","<<dB[1]<<","<<dB[2]<<" u: "<<u[0]<<","<<u[1]<<","<<u[2]<<std::endl;
		}
		Quaternion q_ref(r, f, u);

		Vector3 right(0,0,0), forward(0,0,0), up(0,0,1);
		{
			Vector3 
				pA3 = ProjectionMatrix::GetVectorInCameraSpace(sposA, Sx, Sy), 
				pB3 = ProjectionMatrix::GetVectorInCameraSpace(sposB, Sx, Sy);
			pA3.normalize(); pB3.normalize();
			up = pB3.crossProduct(pA3);			up.normalize();
			forward = pA3 + pB3;	forward.normalize();
			right = forward.crossProduct(up);	right.normalize();
		}
		Quaternion q_compo(right,forward,up);

		return q_ref * q_compo.inverse();
	}

	Quaternion Toric3::_ComputeOrientationForTwoTargets( const Vector3 & campos, const Vector2 & sposA, const Vector2 & sposB, const Vector3 & wposA, const Vector3 & wposB, const double & Sx, const double & Sy )
	{
		Vector3 sposA3(sposA.x(), sposA.y(), 1), sposB3(sposB.x(), sposB.y(), 1);
		return _ComputeOrientationForTwoTargets(campos, sposA3, sposB3, wposA, wposB, Sx, Sy);
	}

	toric::RadianPi Toric3::_getBeta() const
	{
		return getTheta().valueRadians() / 2.;
	}

	const RadianPi & Toric3::getAlpha() const
	{
		return m_alpha;
	}

	Toric3 Toric3::Scale( const Toric3 & reference, const RadianPi & new_alpha )
	{
		Radian2Pi new_theta = ComputeTheta(reference.getThetaRatio(), new_alpha);
		const RadianPi & phi = reference.getPhi();
		return Toric3(new_alpha, new_theta, phi);
	}

}