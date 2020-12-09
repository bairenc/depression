// Code generated by "stringer -type=TimeScales"; DO NOT EDIT.

package leabra

import (
	"errors"
	"strconv"
)

var _ = errors.New("dummy error")

func _() {
	// An "invalid array index" compiler error signifies that the constant values have changed.
	// Re-run the stringer command to generate them again.
	var x [1]struct{}
	_ = x[Cycle-0]
	_ = x[FastSpike-1]
	_ = x[Quarter-2]
	_ = x[Phase-3]
	_ = x[BetaCycle-4]
	_ = x[AlphaCycle-5]
	_ = x[ThetaCycle-6]
	_ = x[Event-7]
	_ = x[Trial-8]
	_ = x[Tick-9]
	_ = x[Sequence-10]
	_ = x[Condition-11]
	_ = x[Block-12]
	_ = x[Epoch-13]
	_ = x[Run-14]
	_ = x[Expt-15]
	_ = x[Scene-16]
	_ = x[Episode-17]
	_ = x[TimeScalesN-18]
}

const _TimeScales_name = "CycleFastSpikeQuarterPhaseBetaCycleAlphaCycleThetaCycleEventTrialTickSequenceConditionBlockEpochRunExptSceneEpisodeTimeScalesN"

var _TimeScales_index = [...]uint8{0, 5, 14, 21, 26, 35, 45, 55, 60, 65, 69, 77, 86, 91, 96, 99, 103, 108, 115, 126}

func (i TimeScales) String() string {
	if i < 0 || i >= TimeScales(len(_TimeScales_index)-1) {
		return "TimeScales(" + strconv.FormatInt(int64(i), 10) + ")"
	}
	return _TimeScales_name[_TimeScales_index[i]:_TimeScales_index[i+1]]
}

func (i *TimeScales) FromString(s string) error {
	for j := 0; j < len(_TimeScales_index)-1; j++ {
		if s == _TimeScales_name[_TimeScales_index[j]:_TimeScales_index[j+1]] {
			*i = TimeScales(j)
			return nil
		}
	}
	return errors.New("String: " + s + " is not a valid option for type: TimeScales")
}
