#!/usr/local/bin/pyleabra -i

# Copyright (c) 2019, The Emergent Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

# to run this python version of the demo:
# * install gopy, currently in fork at https://github.com/goki/gopy
#   e.g., 'go get github.com/goki/gopy -u ./...' and then cd to that package
#   and do 'go install'
# * go to the python directory in this emergent repository, read README.md there, and 
#   type 'make' -- if that works, then type make install (may need sudo)
# * cd back here, and run 'pyemergent' which was installed into /usr/local/bin
# * then type 'import ra25' and this should run
# * you'll need various standard packages such as pandas, numpy, matplotlib, etc

# labra25ra runs a simple random-associator 5x5 = 25 four-layer leabra network

from leabra import go, leabra, emer, eplot, env, agg, patgen, prjn, etable, etensor, params, netview, rand, erand, gi, giv

# this is in-process and will be an installable module under GoGi later
import pygiv

import importlib as il  #il.reload(ra25) -- doesn't seem to work for reasons unknown
import numpy as np
import matplotlib
matplotlib.use('SVG')
#import matplotlib.pyplot as plt
#plt.rcParams['svg.fonttype'] = 'none'  # essential for not rendering fonts as paths
import io

# note: xarray or pytorch TensorDataSet can be used instead of pandas for input / output
# patterns and recording of "log" data for plotting
import pandas as pd

# this will become Sim later.. 
TheSim = 1

# use this for e.g., etable.Column construction args where nil would be passed
nilInts = go.Slice_int()

# use this for e.g., etable.Column construction args where nil would be passed
nilStrs = go.Slice_string()

# note: cannot use method callbacks -- must be separate functions
def InitCB(recv, send, sig, data):
    TheSim.Init()
    TheSim.ClassView.Update()
    TheSim.vp.SetNeedsFullRender()

def TrainCB(recv, send, sig, data):
    if not TheSim.IsRunning:
        TheSim.IsRunning = True
        TheSim.ToolBar.UpdateActions()
        TheSim.Train()

def StopCB(recv, send, sig, data):
    TheSim.Stop()

def StepTrialCB(recv, send, sig, data):
    if not TheSim.IsRunning:
        TheSim.IsRunning = True
        TheSim.TrainTrial()
        TheSim.IsRunning = False
        TheSim.ClassView.Update()
        TheSim.vp.SetNeedsFullRender()

def StepEpochCB(recv, send, sig, data):
    if not TheSim.IsRunning:
        TheSim.IsRunning = True
        TheSim.ToolBar.UpdateActions()
        TheSim.TrainEpoch()

def StepRunCB(recv, send, sig, data):
    if not TheSim.IsRunning:
        TheSim.IsRunning = True
        TheSim.ToolBar.UpdateActions()
        TheSim.TrainRun()

def TestTrialCB(recv, send, sig, data):
    if not TheSim.IsRunning:
        TheSim.IsRunning = True
        TheSim.TestTrial()
        TheSim.IsRunning = False
        TheSim.ClassView.Update()
        TheSim.vp.SetNeedsFullRender()

def TestItemCB(recv, send, sig, data):
    # todo: do full
    if not TheSim.IsRunning:
        TheSim.IsRunning = True
        TheSim.TestTrial()
        TheSim.IsRunning = False
        TheSim.ClassView.Update()
        TheSim.vp.SetNeedsFullRender()

def TestAllCB(recv, send, sig, data):
    if not TheSim.IsRunning:
        TheSim.IsRunning = True
        TheSim.ToolBar.UpdateActions()
        TheSim.RunTestAll()

def ResetRunLogCB(recv, send, sig, data):
    TheSim.RunLog.SetNumRows(0)
    TheSim.RunPlot.Update()

def NewRndSeedCB(recv, send, sig, data):
    TheSim.NewRndSeed()

def ReadmeCB(recv, send, sig, data):
    # todo: add wrapper for oswin.OpenURL so don't need to include it..
    TheSim.NewRndSeed()

def FilterSSE(et, row):
    return et.CellFloat("SSE", row) > 0 # include error trials    

def UpdtFuncNotRunning(act):
    act.SetActiveStateUpdt(not TheSim.IsRunning)
    
def UpdtFuncRunning(act):
    act.SetActiveStateUpdt(TheSim.IsRunning)

# ParamSets is the default set of parameters -- Base is always applied, and others can be optionally
# selected to apply on top of that
ParamSets = params.Sets({
	params.Set(Name="Base", Desc="these are the best params", Sheets=params.Sheets({
		"Network": params.Sheet({
			params.Sel(Sel="Prjn", Desc="norm and momentum on works better, but wt bal is not better for smaller nets",
				Params=params.Params({
					"Prjn.Learn.Norm.On":     "true",
					"Prjn.Learn.Momentum.On": "true",
					"Prjn.Learn.WtBal.On":    "false",
				}).handle),
			params.Sel(Sel="Layer", Desc="using default 1.8 inhib for all of network -- can explore",
				Params=params.Params({
					"Layer.Inhib.Layer.Gi": "1.8",
				}).handle),
			params.Sel(Sel="#Output", Desc="output definitely needs lower inhib -- true for smaller layers in general",
				Params=params.Params({
					"Layer.Inhib.Layer.Gi": "1.4",
				}).handle),
			params.Sel(Sel=".Back", Desc="top-down back-projections MUST have lower relative weight scale, otherwise network hallucinates",
				Params=params.Params({
					"Prjn.WtScale.Rel": "0.2",
				}).handle),
   		}).handle,
		"Sim": params.Sheet({
			params.Sel(Sel="Sim", Desc="best params always finish in this time",
				Params=params.Params({
					"Sim.MaxEpcs": "50",
				}).handle),
		}).handle,
	}).handle),
	params.Set(Name="DefaultInhib", Desc="output uses default inhib instead of lower", Sheets=params.Sheets({
		"Network": params.Sheet({
			params.Sel(Sel="#Output", Desc="go back to default",
				Params=params.Params({
					"Layer.Inhib.Layer.Gi": "1.8",
				}).handle),
		}).handle,
		"Sim": params.Sheet({
			params.Sel(Sel="Sim", Desc="takes longer -- generally doesn't finish..",
				Params=params.Params({
					"Sim.MaxEpcs": "100",
				}).handle),
		}).handle,
	}).handle),
	params.Set(Name="NoMomentum", Desc="no momentum or normalization", Sheets=params.Sheets({
		"Network": params.Sheet({
			params.Sel(Sel="Prjn", Desc="no norm or momentum",
				Params=params.Params({
					"Prjn.Learn.Norm.On":     "false",
					"Prjn.Learn.Momentum.On": "false",
				}).handle),
		}).handle,
	}).handle),
	params.Set(Name="WtBalOn", Desc="try with weight bal on", Sheets=params.Sheets({
		"Network": params.Sheet({
			params.Sel(Sel="Prjn", Desc="weight bal on",
				Params=params.Params({
					"Prjn.Learn.WtBal.On": "true",
				}).handle),
		}).handle,
	}).handle),
})

class Sim(object):
    """
    Sim encapsulates the entire simulation model, and we define all the
    functionality as methods on this struct.  This structure keeps all relevant
    state information organized and available without having to pass everything around
    as arguments to methods, and provides the core GUI interface (note the view tags
    for the fields which provide hints to how things should be displayed).
    """
    def __init__(self):
        self.Net = leabra.Network()
        self.Pats     = etable.Table()
        self.TrnEpcLog   = etable.Table()
        self.TstEpcLog   = etable.Table()
        self.TstTrlLog   = etable.Table()
        self.TstErrLog   = etable.Table()
        self.TstErrStats = etable.Table()
        self.TstCycLog   = etable.Table()
        self.RunLog      = etable.Table()
        self.RunStats    = etable.Table()
        self.Params     = ParamSets
        self.ParamSet = ""
        self.Tag      = ""
        self.MaxRuns  = 10
        self.MaxEpcs  = 50
        self.TrainEnv = env.FixedTable()
        self.TestEnv  = env.FixedTable()
        self.Time     = leabra.Time()
        self.ViewOn   = True
        self.Plot     = True
        self.TrainUpdt = leabra.AlphaCycle
        self.TestUpdt = leabra.Cycle
        self.TestInterval = 5
        
        # statistics
        self.TrlSSE     = 0.0
        self.TrlAvgSSE  = 0.0
        self.TrlCosDiff = 0.0
        self.EpcSSE     = 0.0
        self.EpcAvgSSE  = 0.0
        self.EpcPctErr  = 0.0
        self.EpcPctCor  = 0.0
        self.EpcCosDiff = 0.0
        self.FirstZero  = -1
        
        # internal state - view:"-"
        self.SumSSE     = 0.0
        self.SumAvgSSE  = 0.0
        self.SumCosDiff = 0.0
        self.CntErr     = 0.0
        self.Win        = gi.Window()
        self.vp         = gi.Viewport2D()
        self.ToolBar    = gi.ToolBar()
        self.NetView    = netview.NetView()
        self.TrnEpcPlot = eplot.Plot2D()
        self.TstEpcPlot = eplot.Plot2D()
        self.TstTrlPlot = eplot.Plot2D()
        self.TstCycPlot = eplot.Plot2D()
        self.RunPlot    = eplot.Plot2D()
        self.TrnEpcFile = 0 # todo: file  
        self.RunFile    = 0
        self.SaveWts    = False
        self.NoGui        = False
        self.LogSetParams = False
        self.IsRunning    = False
        self.StopNow    = False
        self.RndSeed    = 0
        
        # ClassView tags for controlling display of fields
        self.Tags = {
            'TrlSSE': 'inactive:"+"',
            'TrlAvgSSE': 'inactive:"+"',
            'TrlCosDiff': 'inactive:"+"',
            'EpcSSE': 'inactive:"+"',
            'EpcAvgSSE': 'inactive:"+"',
            'EpcPctErr': 'inactive:"+"',
            'EpcPctCor': 'inactive:"+"',
            'EpcCosDiff': 'inactive:"+"',
            'FirstZero': 'inactive:"+"',
            'SumSSE': 'view:"-"',
            'SumAvgSSE': 'view:"-"',
            'SumCosDiff': 'view:"-"',
            'CntErr': 'view:"-"',
            'Win': 'view:"-"',
            'vp': 'view:"-"',
            'ToolBar': 'view:"-"',
            'NetView': 'view:"-"',
            'TrnEpcPlot': 'view:"-"',
            'TstEpcPlot': 'view:"-"',
            'TstTrlPlot': 'view:"-"',
            'TstCycPlot': 'view:"-"',
            'RunPlot': 'view:"-"',
            'TrnEpcFile': 'view:"-"',
            'RunFile': 'view:"-"',
            'SaveWts': 'view:"-"',
            'NoGui': 'view:"-"',
            'LogSetParams': 'view:"-"',
            'IsRunning': 'view:"-"',
            'StopNow': 'view:"-"',
            'RndSeed': 'view:"-"',
            'ClassView': 'view:"-"',
            'Tags': 'view:"-"',
        }


    def Config(self):
        """Config configures all the elements using the standard functions"""
        self.OpenPats()
        self.ConfigEnv()
        self.ConfigNet()
        self.ConfigTrnEpcLog()
        self.ConfigTstEpcLog()
        self.ConfigTstTrlLog()
        self.ConfigTstCycLog()
        self.ConfigRunLog()

    def Init(self):
        """Init restarts the run, and initializes everything, including network weights and resets the epoch log table"""
        rand.Seed(self.RndSeed)
        self.ConfigEnv() # just in case another set of pats was selected..
        self.StopNow = False
        self.SetParams("", self.LogSetParams) # all sheets
        self.NewRun()
        self.UpdateView(True)

    def NewRndSeed(self):
        """NewRndSeed gets a new random seed based on current time -- otherwise uses the same random seed for every run"""
        # self.RndSeed = time.Now().UnixNano()

    def Counters(self, train):
        """
        Counters returns a string of the current counter state
        use tabs to achieve a reasonable formatting overall
        and add a few tabs at the end to allow for expansion..
        """
        if train:
            return "Run:\t%d\tEpoch:\t%d\tTrial:\t%d\tName:\t%s\t\t\t" % (self.TrainEnv.Run.Cur, self.TrainEnv.Epoch.Cur, self.TrainEnv.Trial.Cur, self.TrainEnv.TrialName)
        else:
            return "Run:\t%d\tEpoch:\t%d\tTrial:\t%d\tName:\t%s\t\t\t" % (self.TrainEnv.Run.Cur, self.TrainEnv.Epoch.Cur, self.TestEnv.Trial.Cur, self.TestEnv.TrialName)

    def UpdateView(self, train):
        if self.NetView != go.nil:
            # note: essential to use Go version of update when called from another goroutine
            self.NetView.GoUpdate(self.Counters(train)) # note: using counters is significantly slower..

    def AlphaCyc(self, train):
        """
        AlphaCyc runs one alpha-cycle (100 msec, 4 quarters)     of processing.
        External inputs must have already been applied prior to calling,
        using ApplyExt method on relevant layers (see TrainTrial, TestTrial).
        If train is true, then learning DWt or WtFmDWt calls are made.
        Handles netview updating within scope of AlphaCycle
        """
        viewUpdt = self.TrainUpdt
        if not train:
            viewUpdt = self.TestUpdt
        self.Net.AlphaCycInit()
        self.Time.AlphaCycStart()
        for qtr in range(4):
            for cyc in range(self.Time.CycPerQtr):
                self.Net.Cycle(self.Time)
                if not train:
                    self.LogTstCyc(self.Time.Cycle)
                self.Time.CycleInc()
                if self.ViewOn:
                    if viewUpdt == leabra.Cycle:
                        self.UpdateView(train)
                    if viewUpdt == leabra.FastSpike:
                        if (cyc+1)%10 == 0:
                            self.UpdateView(train)
            self.Net.QuarterFinal(self.Time)
            self.Time.QuarterInc()
            if self.ViewOn:
                if viewUpdt == leabra.Quarter:
                    self.UpdateView(train)
                if viewUpdt == leabra.Phase:
                    if qtr >= 2:
                        self.UpdateView(train)
        if train:
            self.Net.DWt()
            self.Net.WtFmDWt()
        if self.ViewOn and viewUpdt == leabra.AlphaCycle:
              self.UpdateView(train)
        if not train:
            self.TstCycPlot.Update()

    def ApplyInputs(self, en):
        """
        ApplyInputs applies input patterns from given environment.
        It is good practice to have this be a separate method with appropriate
        args so that it can be used for various different contexts
        (training, testing, etc).
        """
        self.Net.InitExt() # clear any existing inputs -- not strictly necessary if always
                           # going to the same layers, but good practice and cheap anyway
        inLay = leabra.Layer(self.Net.LayerByName("Input"))
        outLay = leabra.Layer(self.Net.LayerByName("Output"))

        inPats = en.State(inLay.Nm)
        if inPats != go.nil:
            inLay.ApplyExt(inPats)

        outPats = en.State(outLay.Nm)
        if inPats != go.nil:
            outLay.ApplyExt(outPats)
        
        # NOTE: this is how you can use a pandas.DataFrame() to apply inputs
        # we are using etable.Table instead because it provides a full GUI
        # for viewing your patterns, and has a more convenient API, that integrates
        # with the env environment interface.
        #
        # inLay = leabra.Layer(self.Net.LayerByName("Input"))
        # outLay = leabra.Layer(self.Net.LayerByName("Output"))
        # pidx = self.Trial
        # if not self.Sequential:
        #     pidx = self.Porder[self.Trial]
        # # note: these indexes must be updated based on columns in patterns..
        # inp = self.Pats.iloc[pidx,1:26].values
        # outp = self.Pats.iloc[pidx,26:26+25].values
        # self.ApplyExt(inLay, inp)
        # self.ApplyExt(outLay, outp)
        #
        # def ApplyExt(self, lay, nparray):
        # flt = np.ndarray.flatten(nparray, 'C')
        # slc = go.Slice_float32(flt)
        # lay.ApplyExt1D(slc)
    
    def TrainTrial(self):
        """ TrainTrial runs one trial of training using TrainEnv"""
        self.TrainEnv.Step() # the Env encapsulates and manages all counter state

        # Key to query counters FIRST because current state is in NEXT epoch
        # if epoch counter has changed
        epc = env.CounterCur(self.TrainEnv, env.Epoch)
        chg = env.CounterChg(self.TrainEnv, env.Epoch)
        if chg:
            self.LogTrnEpc()
            if self.ViewOn and self.TrainUpdt > leabra.AlphaCycle:
                self.UpdateView(True)
            if epc % self.TestInterval == 0: # note: epc is *next* so won't trigger first time
                self.TestAll()
            if epc >= self.MaxEpcs: # done with training..
                self.RunEnd()
                if self.TrainEnv.Run.Incr(): # we are done!
                    self.StopNow = True
                    return
                else:
                    self.NewRun()
                    return

        self.ApplyInputs(self.TrainEnv)
        self.AlphaCyc(True)   # train
        self.TrialStats(True) # accumulate

    def RunEnd(self):
        """ RunEnd is called at the end of a run -- save weights, record final log, etc here """
        self.LogRun()
        if self.SaveWts:
            fnm = self.WeightsFileName()
            fmt.Printf("Saving Weights to: %v\n", fnm)
            self.Net.SaveWtsJSON(gi.FileName(fnm))

    def NewRun(self):
        """ NewRun intializes a new run of the model, using the TrainEnv.Run counter for the new run value """
        run = self.TrainEnv.Run.Cur
        self.TrainEnv.Init(run)
        self.TestEnv.Init(run)
        self.Time.Reset()
        self.Net.InitWts()
        self.InitStats()
        self.TrnEpcLog.SetNumRows(0)
        self.TstEpcLog.SetNumRows(0)

    def InitStats(self):
        """ InitStats initializes all the statistics, especially important for the
            cumulative epoch stats -- called at start of new run """
        # accumulators
        self.SumSSE = 0
        self.SumAvgSSE = 0
        self.SumCosDiff = 0
        self.CntErr = 0
        self.FirstZero = -1
        # clear rest just to make Sim look initialized
        self.TrlSSE = 0
        self.TrlAvgSSE = 0
        self.EpcSSE = 0
        self.EpcAvgSSE = 0
        self.EpcPctErr = 0
        self.EpcCosDiff = 0
    
    def TrialStats(self, accum):
        """
        TrialStats computes the trial-level statistics and adds them to the epoch accumulators if
        accum is true.  Note that we're accumulating stats here on the Sim side so the
        core algorithm side remains as simple as possible, and doesn't need to worry about
        different time-scales over which stats could be accumulated etc.
        You can also aggregate directly from log data, as is done for testing stats
        """
        outLay = leabra.Layer(self.Net.LayerByName("Output"))
        self.TrlCosDiff = outLay.CosDiff.Cos
        self.TrlSSE = outLay.SSE(0.5) # 0.5 = per-unit tolerance -- right side of .5
        self.TrlAvgSEE = self.TrlSSE / len(outLay.Neurons)
        if accum:
            self.SumSSE += self.TrlSSE
            self.SumAvgSSE += self.TrlAvgSSE
            self.SumCosDiff += self.TrlCosDiff
            if sse != 0:
                self.CntErr += 1.0

    def TrainEpoch(self):
        """ TrainEpoch runs training trials for remainder of this epoch """
        self.StopNow = False
        curEpc = self.TrainEnv.Epoch.Cur
        while True:
            self.TrainTrial()
            if self.StopNow or self.TrainEnv.Epoch.Cur != curEpc:
                break
        self.Stopped()

    def TrainRun(self):
        """ TrainRun runs training trials for remainder of run """
        self.StopNow = False
        curRun = self.TrainEnv.Run.Cur
        while True:
            self.TrainTrial()
            if self.StopNow or self.TrainEnv.Run.Cur != curRun:
                break
        self.Stopped()

    def Train(self):
        """ Train runs the full training from this point onward """
        self.StopNow = False
        while True:
            self.TrainTrial()
            if self.StopNow:
                break
        self.Stopped()

    def Stop(self):
        """ Stop tells the sim to stop running """
        self.StopNow = true

    def Stopped(self):
        """ Stopped is called when a run method stops running -- updates the IsRunning flag and toolbar """
        self.IsRunning = False
        if self.Win != go.nil:
            self.vp.BlockUpdates()
            if self.ToolBar != go.nil:
                self.ToolBar.UpdateActions()
            self.vp.UnblockUpdates()
            self.ClassView.Update()
            self.vp.SetNeedsFullRender()


    ######################################
    #     Testing

    def TestTrial(self):
        """ TestTrial runs one trial of testing -- always sequentially presented inputs """
        self.TestEnv.Step()

        # Query counters FIRST
        chg = env.CounterChg(self.TestEnv, env.Epoch)
        if chg:
            if self.ViewOn and self.TestUpdt > leabra.AlphaCycle:
                self.UpdateView(False)
            self.LogTstEpc()
            return
            
        self.ApplyInputs(self.TestEnv)
        self.AlphaCyc(False)   # !train
        self.TrialStats(False) # !accumulate
        self.LogTstTrl()


    def TestItem(self, idx):
        """ TestItem tests given item which is at given index in test item list """
        cur = self.TestEnv.Trial.Cur
        self.TestEnv.Trial.Cur = idx
        self.TestEnv.SetTrialName()
        self.ApplyInputs(self.TestEnv)
        self.AlphaCyc(False)   # !train
        self.TrialStats(False) # !accumulate
        self.TestEnv.Trial.Cur = cur

    def TestAll(self):
        """ TestAll runs through the full set of testing items """
        self.TestEnv.Init(self.TrainEnv.Run.Cur)
        while True:
            self.TestTrial()
            ch = env.CounterChg(self.TestEnv, env.Epoch)
            if chg or self.StopNow:
                break

    def RunTestAll(self):
        """ RunTestAll runs through the full set of testing items, has stop running = false at end -- for gui """
        self.StopNow = False
        self.TestAll()
        self.Stopped()

    ##########################################
    #   Config methods

    def ConfigEnv(self): 
        if self.MaxRuns == 0: # allow user override
            self.MaxRuns = 10
        if self.MaxEpcs == 0: # allow user override
            self.MaxEpcs = 50
        
        self.TrainEnv.Nm = "TrainEnv"
        self.TrainEnv.Dsc = "training params and state"
        self.TrainEnv.Table = etable.NewIdxView(self.Pats)
        self.TrainEnv.Validate()
        self.TrainEnv.Run.Max = self.MaxRuns # note: we are not setting epoch max -- do that manually
        
        self.TestEnv.Nm = "TestEnv"
        self.TestEnv.Dsc = "testing params and state"
        self.TestEnv.Table = etable.NewIdxView(self.Pats)
        self.TestEnv.Sequential = True
        self.TestEnv.Validate()
        
        # note: to create a train / test split of pats, do this:
        # all = etable.NewIdxView(self.Pats)
        # splits = split.Permuted(all, []float64{.8, .2}, []string{"Train", "Test"})
        # self.TrainEnv.Table = splits.Splits[0]
        # self.TestEnv.Table = splits.Splits[1]
        
        self.TrainEnv.Init(0)
        self.TestEnv.Init(0)

    def ConfigNet(self):
        net = self.Net
        net.InitName(net, "RA25")
        inLay = net.AddLayer2D("Input", 5, 5, emer.Input)
        hid1Lay = net.AddLayer2D("Hidden1", 7, 7, emer.Hidden)
        hid2Lay = net.AddLayer2D("Hidden2", 7, 7, emer.Hidden)
        outLay = net.AddLayer2D("Output", 5, 5, emer.Target)
        
        net.ConnectLayers(inLay, hid1Lay, prjn.NewFull(), emer.Forward)
        net.ConnectLayers(hid1Lay, hid2Lay, prjn.NewFull(), emer.Forward)
        net.ConnectLayers(hid2Lay, outLay, prjn.NewFull(), emer.Forward)
        
        net.ConnectLayers(outLay, hid2Lay, prjn.NewFull(), emer.Back)
        net.ConnectLayers(hid2Lay, hid1Lay, prjn.NewFull(), emer.Back)
        
        net.Defaults()
        self.SetParams("Network", self.LogSetParams) # only set Network params
        net.Build()
        net.InitWts()

    ##########################################
    #   Params methods

    def ParamsName(self):
        """ ParamsName returns name of current set of parameters """
        if self.ParamSet == "":
            return "Base"
        return self.ParamSet

    def SetParams(self, sheet, setMsg):
        """
        SetParams sets the params for "Base" and then current ParamSet.
        If sheet is empty, then it applies all avail sheets (e.g., Network, Sim)
        otherwise just the named sheet
        if setMsg = true then we output a message for each param that was set.
        """
    
        if sheet == "":
            # this is important for catching typos and ensuring that all sheets can be used
            self.Params.ValidateSheets(go.Slice_string(["Network", "Sim"]))
        self.SetParamsSet("Base", sheet, setMsg)
        if self.ParamSet != "" and self.ParamSet != "Base":
            self.SetParamsSet(self.ParamSet, sheet, setMsg)

    def SetParamsSet(self, setNm, sheet, setMsg):
        """
        SetParamsSet sets the params for given params.Set name.
        If sheet is empty, then it applies all avail sheets (e.g., Network, Sim)
        otherwise just the named sheet
        if setMsg = true then we output a message for each param that was set.
        """
        pset = self.Params.SetByNameTry(setNm)
        if pset == go.nil:
            return
        if sheet == "" or sheet == "Network":
            if "Network" in pset.Sheets:
                netp = pset.Sheets["Network"]
                self.Net.ApplyParams(netp, setMsg)
        if sheet == "" or sheet == "Sim":
            if "Sim" in pset.Sheets:
                simp = pset.Sheets["Sim"]
                simp.Apply(self, setMsg)
        # note: if you have more complex environments with parameters, definitely add
        # sheets for them, e.g., "TrainEnv", "TestEnv" etc

    def ConfigPats(self):
        # note: this is all go-based for using etable.Table instead of pandas
        dt = self.Pats
        sc = etable.Schema()
        sc.append(etable.Column("Name", etensor.STRING, nilInts, nilStrs))
        sc.append(etable.Column("Input", etensor.FLOAT32, go.Slice_int([5, 5]), go.Slice_string(["Y", "X"])))
        sc.append(etable.Column("Output", etensor.FLOAT32, go.Slice_int([5, 5]), go.Slice_string(["Y", "X"])))
        dt.SetFromSchema(sc, 25)
            
        patgen.PermutedBinaryRows(dt.Cols[1], 6, 1, 0)
        patgen.PermutedBinaryRows(dt.Cols[2], 6, 1, 0)
        dt.SaveCSV("random_5x5_25_gen.dat", ',', True)

    def OpenPats(self):
        dt = self.Pats
        self.Pats = dt
        dt.SetMetaData("name", "TrainPats")
        dt.SetMetaData("desc", "Training patterns")
        dt.OpenCSV("random_5x5_25.dat", 9) # 9 = tab
        # Note: here's how to read into a pandas DataFrame
        # dt = pd.read_csv("random_5x5_25.dat", sep='\t')
        # dt = dt.drop(columns="_H:")
 
    ##########################################
    #   Logging

    def RunName(self):
        """
        RunName returns a name for this run that combines Tag and Params -- add this to
        any file names that are saved.
        """
        if self.Tag != "":
            return self.Tag + "_" + self.ParamsName()
        else:
            return self.ParamsName()

    def RunEpochName(self, run, epc):
        """
        RunEpochName returns a string with the run and epoch numbers with leading zeros, suitable
        for using in weights file names.  Uses 3, 5 digits for each.
        """
        return "%03d_%05d" % run, epc

    def WeightsFileName(self):
        """ WeightsFileName returns default current weights file name """
        return self.Net.Nm + "_" + self.RunName() + "_" + self.RunEpochName(self.TrainEnv.Run.Cur, self.TrainEnv.Epoch.Cur) + ".wts"

    def LogFileName(self, lognm):
        """ LogFileName returns default log file name """
        return self.Net.Nm + "_" + self.RunName() + "_" + lognm + ".csv"

    #############################
    #   TrnEpcLog
        
    def LogTrnEpc(self):
        """
        LogTrnEpc adds data from current epoch to the TrnEpcLog table
        computes epoch averages prior to logging.
        """
        dt = self.TrnEpcLog
        row = dt.Rows
        self.TrnEpcLog.SetNumRows(row + 1)
        
        hid1Lay = leabra.Layer(self.Net.LayerByName("Hidden1"))
        hid2Lay = leabra.Layer(self.Net.LayerByName("Hidden2"))
        outLay = leabra.Layer(self.Net.LayerByName("Output"))

        epc = self.TrainEnv.Epoch.Prv           # this is triggered by increment so use previous value
        nt = self.TrainEnv.Table.Len() # number of trials in view
        
        self.EpcSSE = self.SumSSE / nt
        self.SumSSE = 0.0
        self.EpcAvgSSE = self.SumAvgSSE / nt
        self.SumAvgSSE = 0.0
        self.EpcPctErr = self.CntErr / nt
        self.CntErr = 0.0
        self.EpcPctCor = 1.0 - self.EpcPctErr
        self.EpcCosDiff = self.SumCosDiff / nt
        self.SumCosDiff = 0.0
        if self.FirstZero < 0 and self.EpcPctErr == 0:
            self.FirstZero = epc

        dt.SetCellFloat("Run", row, self.TrainEnv.Run.Cur)
        dt.SetCellFloat("Epoch", row, epc)
        dt.SetCellFloat("SSE", row, self.EpcSSE)
        dt.SetCellFloat("AvgSSE", row, self.EpcAvgSSE)
        dt.SetCellFloat("PctErr", row, self.EpcPctErr)
        dt.SetCellFloat("PctCor", row, self.EpcPctCor)
        dt.SetCellFloat("CosDiff", row, self.EpcCosDiff)
        dt.SetCellFloat("Hid1 ActAvg", row, hid1Lay.Pools[0].ActAvg.ActPAvgEff)
        dt.SetCellFloat("Hid2 ActAvg", row, hid2Lay.Pools[0].ActAvg.ActPAvgEff)
        dt.SetCellFloat("Out ActAvg", row, outLay.Pools[0].ActAvg.ActPAvgEff)
        
        # note: essential to use Go version of update when called from another goroutine
        self.TrnEpcPlot.GoUpdate()
        if self.TrnEpcFile != go.nil:
            if self.TrainEnv.Run.Cur == 0 and epc == 0:
                dt.WriteCSVHeaders(self.TrnEpcFile, 9) # 9 = tab
            dt.WriteCSVRow(self.TrnEpcFile, row, 9, True) # 9 = tab

        # note: this is how you log to a pandas.DataFrame
        # nwdat = [epc, self.EpcSSE, self.EpcAvgSSE, self.EpcPctErr, self.EpcPctCor, self.EpcCosDiff, 0, 0, 0]
        # nrow = len(self.EpcLog.index)
        # self.EpcLog.loc[nrow] = nwdat # note: this is reportedly rather slow

    def ConfigTrnEpcLog(self):
        dt = self.TrnEpcLog
        dt.SetMetaData("name", "TrnEpcLog")
        dt.SetMetaData("desc", "Record of performance over epochs of training")
        dt.SetMetaData("read-only", "true")
        
        sc = etable.Schema()
        sc.append(etable.Column("Run", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("Epoch", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("SSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("AvgSSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("PctErr", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("PctCor", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("CosDiff", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid1 ActAvg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid2 ActAvg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Out ActAvg", etensor.FLOAT64, nilInts, nilStrs))
        dt.SetFromSchema(sc, 0)
        
        # note: pandas.DataFrame version
        # self.EpcLog = pd.DataFrame(columns=["Epoch", "SSE", "Avg SSE", "Pct Err", "Pct Cor", "CosDiff", "Hid1 ActAvg", "Hid2 ActAvg", "Out ActAvg"])
        # self.PlotVals = ["SSE", "Pct Err"]
        # self.Plot = True

    def ConfigTrnEpcPlot(self):
        plt = self.TrnEpcPlot
        plt.Params.Title = "Leabra Random Associator 25 Epoch Plot"
        plt.Params.XAxisCol = "Epoch"
        # order of params: on, fixMin, min, fixMax, max
        plt.SetColParams("Run", False, True, 0, False, 0)
        plt.SetColParams("Epoch", False, True, 0, False, 0)
        plt.SetColParams("SSE", False, True, 0, False, 0)
        plt.SetColParams("AvgSSE", False, True, 0, False, 0)
        plt.SetColParams("PctErr", True, True, 0, True, 1) # default plot
        plt.SetColParams("PctCor", True, True, 0, True, 1) # default plot
        plt.SetColParams("CosDiff", False, True, 0, True, 1)
        plt.SetColParams("Hid1 ActAvg", False, True, 0, True, .5)
        plt.SetColParams("Hid2 ActAvg", False, True, 0, True, .5)
        plt.SetColParams("Out ActAvg", False, True, 0, True, .5)

    #############################
    #   TstTrlLog
        
    def LogTstTrl(self):
        """
        LogTstTrl adds data from current epoch to the TstTrlLog table
        log always contains number of testing items
        """
        dt = self.TstTrlLog

        inLay = leabra.Layer(self.Net.LayerByName("Input"))
        hid1Lay = leabra.Layer(self.Net.LayerByName("Hidden1"))
        hid2Lay = leabra.Layer(self.Net.LayerByName("Hidden2"))
        outLay = leabra.Layer(self.Net.LayerByName("Output"))

        epc = self.TrainEnv.Epoch.Prv           # this is triggered by increment so use previous value
        trl = self.TestEnv.Trial.Cur  
        
        dt.SetCellFloat("Epoch", trl, epc)
        dt.SetCellFloat("Trial", trl, trl)
        dt.SetCellString("TrialName", trl, self.TestEnv.TrialName)
        dt.SetCellFloat("SSE", trl, self.TrlSSE)
        dt.SetCellFloat("AvgSSE", trl, self.TrlAvgSSE)
        dt.SetCellFloat("CosDiff", trl, self.TrlCosDiff)
        dt.SetCellFloat("Hid1 ActM.Avg", trl, hid1Lay.Pools[0].ActM.Avg)
        dt.SetCellFloat("Hid2 ActM.Avg", trl, hid2Lay.Pools[0].ActM.Avg)
        dt.SetCellFloat("Out ActM.Avg", trl, outLay.Pools[0].ActM.Avg)
        
        dt.SetCellTensor("InAct", trl, inLay.UnitValsTensor("Act"))
        dt.SetCellTensor("OutActM", trl, outLay.UnitValsTensor("ActM"))
        dt.SetCellTensor("OutActP", trl, outLay.UnitValsTensor("ActP"))
        
        # note: essential to use Go version of update when called from another goroutine
        self.TstTrlPlot.GoUpdate()

    def ConfigTstTrlLog(self):
        inLay = leabra.Layer(self.Net.LayerByName("Input"))
        outLay = leabra.Layer(self.Net.LayerByName("Output"))
        
        dt = self.TstTrlLog
        dt.SetMetaData("name", "TstTrlLog")
        dt.SetMetaData("desc", "Record of testing per input pattern")
        dt.SetMetaData("read-only", "true")
        
        sc = etable.Schema()
        sc.append(etable.Column("Run", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("Epoch", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("Trial", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("TrialName", etensor.STRING, nilInts, nilStrs))
        sc.append(etable.Column("SSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("AvgSSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("CosDiff", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid1 ActM.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid2 ActM.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Out ActM.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("InAct", etensor.FLOAT64, inLay.Shp.Shp, nilStrs))
        sc.append(etable.Column("OutActM", etensor.FLOAT64, outLay.Shp.Shp, nilStrs))
        sc.append(etable.Column("OutActP", etensor.FLOAT64, outLay.Shp.Shp, nilStrs))
        dt.SetFromSchema(sc, 0)
        

    def ConfigTstTrlPlot(self):
        plt = self.TstTrlPlot
        plt.Params.Title = "Leabra Random Associator 25 Test Trial Plot"
        plt.Params.XAxisCol = "Trial"
        # order of params: on, fixMin, min, fixMax, max
        plt.SetColParams("Run", False, True, 0, False, 0)
        plt.SetColParams("Epoch", False, True, 0, False, 0)
        plt.SetColParams("Trial", False, True, 0, False, 0)
        plt.SetColParams("TrialName", False, True, 0, False, 0)
        plt.SetColParams("SSE", False, True, 0, False, 0)
        plt.SetColParams("AvgSSE", False, True, 0, False, 0)
        plt.SetColParams("CosDiff", True, True, 0, True, 1)
        plt.SetColParams("Hid1 ActAvg", True, True, 0, True, .5)
        plt.SetColParams("Hid2 ActAvg", True, True, 0, True, .5)
        plt.SetColParams("Out ActAvg", True, True, 0, True, .5)

        plt.SetColParams("InAct", False, True, 0, True, 1)
        plt.SetColParams("OutActM", False, True, 0, True, 1)
        plt.SetColParams("OutActP", False, True, 0, True, 1)
        
    #############################
    #   TstEpcLog
        
    def LogTstEpc(self):
        """
        LogTstEpc adds data from current epoch to the TstEpcLog table
        log always contains number of testing items
        """
        dt = self.TstEpcLog
        row = dt.Rows
        dt.SetNumRows(row + 1)

        trl = self.TstTrlLog
        tix = etable.NewIdxView(trl)
        epc = self.TrainEnv.Epoch.Prv

        # note: this shows how to use agg methods to compute summary data from another
        # data table, instead of incrementing on the Sim
        dt.SetCellFloat("Run", row, self.TrainEnv.Run.Cur)
        dt.SetCellFloat("Epoch", row, epc)
        dt.SetCellFloat("SSE", row, agg.Sum(tix, "SSE")[0])
        dt.SetCellFloat("AvgSSE", row, agg.Mean(tix, "AvgSSE")[0])
        dt.SetCellFloat("PctErr", row, agg.PropIf(tix, "SSE", lambda idx, val: val > 0)[0])
        dt.SetCellFloat("PctCor", row, agg.PropIf(tix, "SSE", lambda idx, val: val == 0)[0])
        dt.SetCellFloat("CosDiff", row, agg.Mean(tix, "CosDiff")[0])
        
        trlix = etable.NewIdxView(trl)
        trlix.Filter(FilterSSE)
        
        self.TstErrLog = trlix.NewTable()
        
        allsp = split.All(trlix)
        split.Agg(allsp, "SSE", agg.AggSum)
        split.Agg(allsp, "AvgSSE", agg.AggMean)
        split.Agg(allsp, "InAct", agg.AggMean)
        split.Agg(allsp, "OutActM", agg.AggMean)
        split.Agg(allsp, "OutActP", agg.AggMean)
        
        self.TstErrStats = allsp.AggsToTable(False)
        
        # note: essential to use Go version of update when called from another goroutine
        self.TstEpcPlot.GoUpdate()

    def ConfigTstEpcLog(self):
        dt = self.TstEpcLog
        dt.SetMetaData("name", "TstEpcLog")
        dt.SetMetaData("desc", "Summary stats for testing trials")
        dt.SetMetaData("read-only", "true")
        
        sc = etable.Schema()
        sc.append(etable.Column("Run", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("Epoch", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("SSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("AvgSSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("PctErr", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("PctCor", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("CosDiff", etensor.FLOAT64, nilInts, nilStrs))
        dt.SetFromSchema(sc, 0)
        

    def ConfigTstEpcPlot(self):
        plt = self.TstEpcPlot
        plt.Params.Title = "Leabra Random Associator 25 Testing Epoch Plot"
        plt.Params.XAxisCol = "Epoch"
        # order of params: on, fixMin, min, fixMax, max
        plt.SetColParams("Run", False, True, 0, False, 0)
        plt.SetColParams("Epoch", False, True, 0, False, 0)
        plt.SetColParams("SSE", False, True, 0, False, 0)
        plt.SetColParams("AvgSSE", False, True, 0, False, 0)
        plt.SetColParams("PctErr", True, True, 0, True, 1) # default plot
        plt.SetColParams("PctCor", True, True, 0, True, 1) # default plot
        plt.SetColParams("CosDiff", False, True, 0, True, 1)
        
    #############################
    #   TstCycLog
        
    def LogTstCyc(self, cyc):
        """
        LogTstCyc adds data from current trial to the TstCycLog table.
        log just has 100 cycles, is overwritten
        """
        dt = self.TstCycLog
        if dt.Rows <= cyc:
            dt.SetNumRows(cyc + 1)
        
        hid1Lay = leabra.Layer(self.Net.LayerByName("Hidden1"))
        hid2Lay = leabra.Layer(self.Net.LayerByName("Hidden2"))
        outLay = leabra.Layer(self.Net.LayerByName("Output"))
        
        dt.SetCellFloat("Cycle", cyc, cyc)
        dt.SetCellFloat("Hid1 Ge.Avg", cyc, hid1Lay.Pools[0].Ge.Avg)
        dt.SetCellFloat("Hid2 Ge.Avg", cyc, hid2Lay.Pools[0].Ge.Avg)
        dt.SetCellFloat("Out Ge.Avg", cyc, outLay.Pools[0].Ge.Avg)
        dt.SetCellFloat("Hid1 Act.Avg", cyc, hid1Lay.Pools[0].Act.Avg)
        dt.SetCellFloat("Hid2 Act.Avg", cyc, hid2Lay.Pools[0].Act.Avg)
        dt.SetCellFloat("Out Act.Avg", cyc, outLay.Pools[0].Act.Avg)
        
        if cyc % 10 == 0: # too slow to do every cyc
            # note: essential to use Go version of update when called from another goroutine
            self.TstCycPlot.GoUpdate()

    def ConfigTstCycLog(self):
        dt = self.TstCycLog
        dt.SetMetaData("name", "TstCycLog")
        dt.SetMetaData("desc", "Record of activity etc over one trial by cycle")
        dt.SetMetaData("read-only", "true")
        np = 100 # max cycles
        
        sc = etable.Schema()
        sc.append(etable.Column("Cycle", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid1 Ge.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid2 Ge.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Out Ge.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid1 Act.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Hid2 Act.Avg", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("Out Act.Avg", etensor.FLOAT64, nilInts, nilStrs))
        dt.SetFromSchema(sc, np)
        
    def ConfigTstCycPlot(self):
        plt = self.TstCycPlot
        plt.Params.Title = "Leabra Random Associator 25 Test Cycle Plot"
        plt.Params.XAxisCol = "Cycle"
        # order of params: on, fixMin, min, fixMax, max
        plt.SetColParams("Cycle", False, True, 0, False, 0)
        plt.SetColParams("Hid1 Ge.Avg", True, True, 0, True, .5)
        plt.SetColParams("Hid2 Ge.Avg", True, True, 0, True, .5)
        plt.SetColParams("Out Ge.Avg", True, True, 0, True, .5)
        plt.SetColParams("Hid1 Act.Avg", True, True, 0, True, .5)
        plt.SetColParams("Hid2 Act.Avg", True, True, 0, True, .5)
        plt.SetColParams("Out Act.Avg", True, True, 0, True, .5)

    #############################
    #   RunLog
        
    def LogRun(self):
        dt = self.RunLog
        run = self.TrainEnv.Run.Cur # this is NOT triggered by increment yet -- use Cur
        row = dt.Rows
        self.RunLog.SetNumRows(row + 1)
        
        epclog = self.TrnEpcLog
        # compute mean over last N epochs for run level
        nlast = 10
        epcix = etable.NewIdxView(epclog)
        epcix.Idxs = epcix.Idxs[epcix.Len()-nlast-1:]
        
        params = self.ParamsName()
        
        dt.SetCellFloat("Run", row, run)
        dt.SetCellString("Params", row, params)
        dt.SetCellFloat("FirstZero", row, self.FirstZero)
        dt.SetCellFloat("SSE", row, agg.Mean(epcix, "SSE")[0])
        dt.SetCellFloat("AvgSSE", row, agg.Mean(epcix, "AvgSSE")[0])
        dt.SetCellFloat("PctErr", row, agg.Mean(epcix, "PctErr")[0])
        dt.SetCellFloat("PctCor", row, agg.Mean(epcix, "PctCor")[0])
        dt.SetCellFloat("CosDiff", row, agg.Mean(epcix, "CosDiff")[0])
        
        runix = etable.NewIdxView(dt)
        spl = split.GroupBy(runix, go.Slice_string(["Params"]))
        split.Desc(spl, "FirstZero")
        split.Desc(spl, "PctCor")
        self.RunStats = spl.AggsToTable(False)
        
        # note: essential to use Go version of update when called from another goroutine
        self.RunPlot.GoUpdate()
        if self.RunFile != go.nil:
            if row == 0:
                dt.WriteCSVHeaders(self.RunFile, 9) # 9 = tab
            dt.WriteCSVRow(self.RunFile, row, 9, True) # 9 = tab
            
    def ConfigRunLog(self):
        dt = self.RunLog
        dt.SetMetaData("name", "RunLog")
        dt.SetMetaData("desc", "Record of performance at end of training")
        dt.SetMetaData("read-only", "true")
        sc = etable.Schema()
        sc.append(etable.Column("Run", etensor.INT64, nilInts, nilStrs))
        sc.append(etable.Column("Params", etensor.STRING, nilInts, nilStrs))
        sc.append(etable.Column("FirstZero", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("SSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("AvgSSE", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("PctErr", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("PctCor", etensor.FLOAT64, nilInts, nilStrs))
        sc.append(etable.Column("CosDiff", etensor.FLOAT64, nilInts, nilStrs))
        dt.SetFromSchema(sc, 0)

    def ConfigRunPlot(self):
        plt = self.RunPlot
        plt.Params.Title = "Leabra Random Associator 25 Run Plot"
        plt.Params.XAxisCol = "Run"
        # order of params: on, fixMin, min, fixMax, max
        plt.SetColParams("Run", False, True, 0, False, 0)
        plt.SetColParams("FirstZero", True, True, 0, False, 0) # default plot
        plt.SetColParams("SSE", False, True, 0, False, 0)
        plt.SetColParams("AvgSSE", False, True, 0, False, 0)
        plt.SetColParams("PctErr", False, True, 0, True, 1)
        plt.SetColParams("PctCor", False, True, 0, True, 1)
        plt.SetColParams("CosDiff", False, True, 0, True, 1)

    ##############################
    #   ConfigGui

    def ConfigGui(self):
        """ConfigGui configures the GoGi gui interface for this simulation"""
        width = 1600
        height = 1200
        
        gi.SetAppName("ra25")
        gi.SetAppAbout('This demonstrates a basic Leabra model. See <a href="https://github.com/emer/emergent">emergent on GitHub</a>.</p>')
        
        win = gi.NewWindow2D("ra25", "Leabra Random Associator", width, height, True)
        self.Win = win

        vp = win.WinViewport2D()
        self.vp = vp
        updt = vp.UpdateStart()
         
        mfr = win.SetMainFrame()
        
        tbar = gi.AddNewToolBar(mfr, "tbar")
        tbar.SetStretchMaxWidth()
        self.ToolBar = tbar
        
        split = gi.AddNewSplitView(mfr, "split")
        split.Dim = gi.X
        split.SetStretchMaxWidth()
        split.SetStretchMaxHeight()
         
        self.ClassView = pygiv.ClassView("ra25sv", self.Tags)
        self.ClassView.AddFrame(split)
        self.ClassView.SetClass(self)

        tv = gi.AddNewTabView(split, "tv")
        
        nv = netview.NetView()
        tv.AddTab(nv, "NetView")
        nv.Var = "Act"
        nv.SetNet(self.Net)
        self.NetVew = nv
        
        plt = eplot.Plot2D()
        tv.AddTab(plt, "TrnEpcPlot")
        plt.Params.XAxisCol = "Epoch"
        plt.SetTable(self.TrnEpcLog)
        self.TrnEpcPlot = plt
        self.ConfigTrnEpcPlot()
        
        plt = eplot.Plot2D()
        tv.AddTab(plt, "TstTrlPlot")
        plt.Params.XAxisCol = "Trial"
        plt.SetTable(self.TstTrlLog)
        self.TstTrlPlot = plt
        self.ConfigTstTrlPlot()
        
        plt = eplot.Plot2D()
        tv.AddTab(plt, "TstCycPlot")
        plt.Params.XAxisCol = "Cycle"
        plt.SetTable(self.TstCycLog)
        self.TstCycPlot = plt
        self.ConfigTstCycPlot()
        
        plt = eplot.Plot2D()
        tv.AddTab(plt, "TstEpcPlot")
        plt.Params.XAxisCol = "Epoch"
        plt.SetTable(self.TstEpcLog)
        self.TstEpcPlot = plt
        self.ConfigTstEpcPlot()
        
        plt = eplot.Plot2D()
        tv.AddTab(plt, "RunPlot")
        plt.Params.XAxisCol = "Run"
        plt.SetTable(self.RunLog)
        self.RunPlot = plt
        self.ConfigRunPlot()

        split.SetSplitsList(go.Slice_float32([.3, .7]))
        
        recv = win.This()
        
        tbar.AddAction(gi.ActOpts(Label="Init", Icon="update", Tooltip="Initialize everything including network weights, and start over.  Also applies current params.", UpdateFunc=UpdtFuncNotRunning), recv, InitCB)

        tbar.AddAction(gi.ActOpts(Label="Train", Icon="run", Tooltip="Starts the network training, picking up from wherever it may have left off.  If not stopped, training will complete the specified number of Runs through the full number of Epochs of training, with testing automatically occuring at the specified interval.", UpdateFunc=UpdtFuncNotRunning), recv, TrainCB)
        
        tbar.AddAction(gi.ActOpts(Label="Stop", Icon="stop", Tooltip="Interrupts running.  Hitting Train again will pick back up where it left off.", UpdateFunc=UpdtFuncRunning), recv, StopCB)
        
        tbar.AddAction(gi.ActOpts(Label="Step Trial", Icon="step-fwd", Tooltip="Advances one training trial at a time.", UpdateFunc=UpdtFuncNotRunning), recv, StepTrialCB)
        
        tbar.AddAction(gi.ActOpts(Label="Step Epoch", Icon="fast-fwd", Tooltip="Advances one epoch (complete set of training patterns) at a time.", UpdateFunc=UpdtFuncNotRunning), recv, StepEpochCB)

        tbar.AddAction(gi.ActOpts(Label="Step Run", Icon="fast-fwd", Tooltip="Advances one full training Run at a time.", UpdateFunc=UpdtFuncNotRunning), recv, StepRunCB)
        
        tbar.AddSeparator("test")
        
        tbar.AddAction(gi.ActOpts(Label="Test Trial", Icon="step-fwd", Tooltip="Runs the next testing trial.", UpdateFunc=UpdtFuncNotRunning), recv, TestTrialCB)
        
        tbar.AddAction(gi.ActOpts(Label="Test Item", Icon="step-fwd", Tooltip="Prompts for a specific input pattern name to run, and runs it in testing mode.", UpdateFunc=UpdtFuncNotRunning), recv, TestItemCB)
        
        tbar.AddAction(gi.ActOpts(Label="Test All", Icon="fast-fwd", Tooltip="Tests all of the testing trials.", UpdateFunc=UpdtFuncNotRunning), recv, TestAllCB)

        tbar.AddSeparator("log")
        
        tbar.AddAction(gi.ActOpts(Label="Reset RunLog", Icon="reset", Tooltip="Resets the accumulated log of all Runs, which are tagged with the ParamSet used"), recv, ResetRunLogCB)

        tbar.AddSeparator("misc")
        
        tbar.AddAction(gi.ActOpts(Label="New Seed", Icon="new", Tooltip="Generate a new initial random seed to get different results.  By default, Init re-establishes the same initial seed every time."), recv, NewRndSeedCB)

        tbar.AddAction(gi.ActOpts(Label="README", Icon="file-markdown", Tooltip="Opens your browser on the README file that contains instructions for how to run this model."), recv, ReadmeCB)
        
        # main menu
        appnm = gi.AppName()
        mmen = win.MainMenu
        mmen.ConfigMenus(go.Slice_string([appnm, "File", "Edit", "Window"]))
        
        amen = gi.Action(win.MainMenu.ChildByName(appnm, 0))
        amen.Menu.AddAppMenu(win)
        
        emen = gi.Action(win.MainMenu.ChildByName("Edit", 1))
        emen.Menu.AddCopyCutPaste(win)
        
        # note: Command in shortcuts is automatically translated into Control for
        # Linux, Windows or Meta for MacOS
        # fmen = win.MainMenu.ChildByName("File", 0).(*gi.Action)
        # fmen.Menu = make(gi.Menu, 0, 10)
        # fmen.Menu.AddAction(gi.ActOpts{Label: "Open", Shortcut: "Command+O"},
        #     recv, func(recv, send ki.Ki, sig int64, data interface{}) {
        #     FileViewOpenSVG(vp)
        #     })
        # fmen.Menu.AddSeparator("csep")
        # fmen.Menu.AddAction(gi.ActOpts{Label: "Close Window", Shortcut: "Command+W"},
        #     recv, func(recv, send ki.Ki, sig int64, data interface{}) {
        #     win.CloseReq()
        #     })
                
        #    win.SetCloseCleanFunc(func(w *gi.Window) {
        #         gi.Quit() # once main window is closed, quit
        #     })
        #         
        win.MainMenuUpdated()
        vp.UpdateEndNoSig(updt)
        win.GoStartEventLoop()
        

# TheSim is the overall state for this simulation
TheSim = Sim()

TheSim.Config()
TheSim.Init()
TheSim.ConfigGui()
# TheSim.Train()
# TheSim.EpcLog.SaveCSV("ra25_epc.dat", ord(','), True)

    