
#include "Toric.h"

namespace toric
{

	Toric3::Toric3(const RadianPi & alpha, const Radian2Pi & theta, const RadianPi & phi)
	{
		m_alpha = alpha;
	}

	const RadianPi & Toric3::getAlpha() const
	{
		return m_alpha;
	}

	Toric3 Toric3::FromWorldPosition( const Vector3 & wposP, const Vector3 & wposA, const Vector3 & wposB)
	{

		Toric3 res(1, 1, 1);

		return res;
	}
}