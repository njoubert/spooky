
#ifndef TORIC_TORIC_H
#define TORIC_TORIC_H

#include "Euler.h"
#include "Vector.h"

#include <vector>

namespace toric
{

	class Toric3 
	{
	private:
		RadianPi m_alpha;

	public:	
		Toric3(const RadianPi & alpha, const Radian2Pi & theta, const RadianPi & phi);
		const RadianPi & getAlpha() const;

		static Toric3  FromWorldPosition(const Vector3 & wpos, const Vector3 & wposA, const Vector3 & wposB);

	};

}

#endif