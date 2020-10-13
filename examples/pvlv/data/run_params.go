// Copyright (c) 2020, The Emergent Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

package data

// A sequence of runs (each step is a RunBlockParams object)
type RunParams struct {
	Nm       string `desc:"Name of the sequence"`
	Desc     string `desc:"Description"`
	Block1Nm string `desc:"name of run block 1"`
	Block2Nm string `desc:"name of run block 2"`
	Block3Nm string `desc:"name of run block 3"`
	Block4Nm string `desc:"name of run block 4"`
	Block5Nm string `desc:"name of run block 5"`
}
type RunParamsMap map[string]RunParams

func AllRunParams() RunParamsMap {
	seqs := map[string]RunParams{
		"RunMaster": {
			Nm:       "RunMaster",
			Desc:     "",
			Block1Nm: "PosAcq_B50",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"USDebug": {
			Nm:       "USDebug",
			Desc:     "",
			Block1Nm: "USDebug",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"US0": {
			Nm:       "US0",
			Desc:     "",
			Block1Nm: "US0",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcq_A50": {
			Nm:       "PosAcq_A50",
			Desc:     "",
			Block1Nm: "PosAcq_A50",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcq_B50Ext": {
			Nm:       "PosAcq_B50Ext",
			Desc:     "",
			Block1Nm: "PosAcq_B50",
			Block2Nm: "PosExtinct",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcq_B50ExtAcq": {
			Nm:       "PosAcq_B50ExtAcq",
			Desc:     "Full cycle: acq, ext, acq",
			Block1Nm: "PosAcq_B50",
			Block2Nm: "PosExtinct",
			Block3Nm: "PosAcq_B50Cont",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcq_B100Ext": {
			Nm:       "PosAcq_B100Ext",
			Desc:     "",
			Block1Nm: "PosAcq_B100",
			Block2Nm: "PosExtinct",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcq": {
			Nm:       "PosAcq",
			Desc:     "",
			Block1Nm: "PosAcq_B50",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosExt": {
			Nm:       "PosExt",
			Desc:     "",
			Block1Nm: "PosAcq_B50",
			Block2Nm: "PosExtinct",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcq_B25": {
			Nm:       "PosAcq_B25",
			Desc:     "",
			Block1Nm: "PosAcq_B25",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"NegAcq": {
			Nm:       "NegAcq",
			Desc:     "",
			Block1Nm: "NegAcq",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"NegAcqMag": {
			Nm:       "NegAcqMag",
			Desc:     "",
			Block1Nm: "NegAcqMag",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcqMag": {
			Nm:       "PosAcqMag",
			Desc:     "",
			Block1Nm: "PosAcqMag",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"NegAcqExt": {
			Nm:       "NegAcqExt",
			Desc:     "",
			Block1Nm: "NegAcq",
			Block2Nm: "NegExtinct",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosCondInhib": {
			Nm:       "PosCondInhib",
			Desc:     "",
			Block1Nm: "PosAcq_contextA",
			Block2Nm: "PosCondInhib",
			Block3Nm: "PosCondInhib_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosSecondOrderCond": {
			Nm:       "PosSecondOrderCond",
			Desc:     "",
			Block1Nm: "PosAcqPreSecondOrder",
			Block2Nm: "PosSecondOrderCond",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosBlocking": {
			Nm:       "PosBlocking",
			Desc:     "",
			Block1Nm: "PosBlocking_A_training",
			Block2Nm: "PosBlocking",
			Block3Nm: "PosBlocking_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosBlocking2": {
			Nm:       "PosBlocking2",
			Desc:     "",
			Block1Nm: "PosBlocking_A_training",
			Block2Nm: "PosBlocking",
			Block3Nm: "PosBlocking2_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"NegCondInhib": {
			Nm:       "NegCondInhib",
			Desc:     "",
			Block1Nm: "NegAcq",
			Block2Nm: "NegCondInh",
			Block3Nm: "NegCondInh_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"AbaRenewal": {
			Nm:       "AbaRenewal",
			Desc:     "",
			Block1Nm: "PosAcq_contextA",
			Block2Nm: "PosExtinct_contextB",
			Block3Nm: "PosRenewal_contextA",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"NegBlocking": {
			Nm:       "NegBlocking",
			Desc:     "",
			Block1Nm: "NegBlocking_E_training",
			Block2Nm: "NegBlocking",
			Block3Nm: "NegBlocking_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosSum_test": {
			Nm:       "PosSum_test",
			Desc:     "",
			Block1Nm: "PosSumAcq",
			Block2Nm: "PosSumCondInhib",
			Block3Nm: "PosSum_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"NegSum_test": {
			Nm:       "NegSum_test",
			Desc:     "",
			Block1Nm: "NegSumAcq",
			Block2Nm: "NegSumCondInhib",
			Block3Nm: "NegSum_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"UnblockingValue": {
			Nm:       "UnblockingValue",
			Desc:     "",
			Block1Nm: "Unblocking_train",
			Block2Nm: "UnblockingValue",
			Block3Nm: "UnblockingValue_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"UnblockingIdentity": {
			Nm:       "UnblockingIdentity",
			Desc:     "",
			Block1Nm: "Unblocking_trainUS",
			Block2Nm: "UnblockingIdentity",
			Block3Nm: "UnblockingIdentity_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"Overexpect": {
			Nm:       "Overexpect",
			Desc:     "",
			Block1Nm: "Overexpect_train",
			Block2Nm: "OverexpectCompound",
			Block3Nm: "Overexpect_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosMagChange": {
			Nm:       "PosMagChange",
			Desc:     "",
			Block1Nm: "PosAcqMag",
			Block2Nm: "PosAcqMagChange",
			Block3Nm: "Overexpect_test",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"NegMagChange": {
			Nm:       "NegMagChange",
			Desc:     "",
			Block1Nm: "NegAcqMag",
			Block2Nm: "NegAcqMagChange",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"CondExp": {
			Nm:       "CondExp",
			Desc:     "",
			Block1Nm: "CondExp",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PainExp": {
			Nm:       "PainExp",
			Desc:     "",
			Block1Nm: "PainExp",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosNeg": {
			Nm:       "PosNeg",
			Desc:     "",
			Block1Nm: "PosOrNegAcq",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosAcqEarlyUSTest": {
			Nm:       "PosAcqEarlyUSTest",
			Desc:     "",
			Block1Nm: "PosAcq_B50",
			Block2Nm: "PosAcqEarlyUS_test",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"AutomatedTesting": {
			Nm:       "AutomatedTesting",
			Desc:     "This paramset is just for naming purposes",
			Block1Nm: "NullStep",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosOrNegAcq": {
			Nm:       "PosOrNegAcq",
			Desc:     "",
			Block1Nm: "PosOrNegAcq",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
		"PosCondInhib_test": {
			Nm:       "PosCondInhib_test",
			Desc:     "For debugging",
			Block1Nm: "PosCondInhib_test",
			Block2Nm: "NullStep",
			Block3Nm: "NullStep",
			Block4Nm: "NullStep",
			Block5Nm: "NullStep",
		},
	}

	return seqs
}
