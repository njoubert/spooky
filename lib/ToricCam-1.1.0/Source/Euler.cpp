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

#include "toric/Euler.h"

#include <math.h>

namespace toric
{
	/************************************************************************/
	/* RadianPi                                                               */
	/************************************************************************/

	RadianPi RadianPi::ZERO(0);

	RadianPi::RadianPi( const double & r ) : m_value(r) { m_value = _modulo(m_value); }

	const double & RadianPi::valueRadians() const { return m_value; }

	double RadianPi::valueDegrees() const { return (m_value * 360.) / TWO_PI; }

	RadianPi RadianPi::operator*( double const& val) const { return RadianPi( m_value * val ); }
	RadianPi RadianPi::operator/( double const& val ) const { return RadianPi( m_value / val ); }

	double RadianPi::_modulo( const double & d )
	{
		if( fabs(d) - PI < 1e-5 ) return d;

		double result(d);
		
		int n1 = 0, n2 = 0;
		if( result < - PI )
		{
			n1 = (int) -floor((result+PI) / TWO_PI);
			result = result + (n1 * TWO_PI);
		}
		
		if( result > PI )
		{		
			n2 = (int) ceil( (result-PI) / TWO_PI);
			result = result - (n2 * TWO_PI);
		}

		return result;
	}

	/************************************************************************/
	/* Radian2Pi                                                              */
	/************************************************************************/

	Radian2Pi Radian2Pi::ZERO(0);

	Radian2Pi::Radian2Pi( const double & r ) : m_value(r) { m_value = _modulo(m_value); }

	const double & Radian2Pi::valueRadians() const { return m_value; }

	double Radian2Pi::valueDegrees() const { return (m_value * 360.) / TWO_PI; }

	double Radian2Pi::_modulo( const double & d )
	{
		if( d > -1e-5 && d < TWO_PI + 1e-5) return d;

		double result(d);

		int n1 = 0, n2 = 0;
		if( result < 0 )
		{
			n1 = (int) ceil(-result / TWO_PI);
			result = result + (n1 * TWO_PI);
		}

		if( result > TWO_PI )
		{		
			n2 = (int) floor(result / TWO_PI);
			result = result - (n2 * TWO_PI);
		}

		return result;
	}
}

double cos( const toric::RadianPi & r )
{
	return cos(r.valueRadians());
}

double sin( const toric::RadianPi & r )
{
	return sin(r.valueRadians());
}

double tan( const toric::RadianPi & r )
{
	return tan(r.valueRadians());
}

double acos( const toric::RadianPi & r )
{
	return acos(r.valueRadians());
}

double asin( const toric::RadianPi & r )
{
	return asin(r.valueRadians());
}

double atan( const toric::RadianPi & r )
{
	return atan(r.valueRadians());
}