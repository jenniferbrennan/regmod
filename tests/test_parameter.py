"""
Test parameter module
"""
import pytest
import numpy as np
import pandas as pd
from regmod.data import Data
from regmod.prior import GaussianPrior, UniformPrior, SplineGaussianPrior, SplineUniformPrior
from regmod.variable import Variable, SplineVariable
from regmod.parameter import Parameter
from regmod.utils import SplineSpecs


@pytest.fixture
def data():
    num_obs = 5
    df = pd.DataFrame({
        "obs": np.random.randn(num_obs),
        "cov0": np.random.randn(num_obs),
        "cov1": np.random.randn(num_obs)
    })
    return Data(col_obs="obs",
                col_covs=["cov0", "cov1"],
                df=df)


@pytest.fixture
def gprior():
    return GaussianPrior(mean=0.0, sd=1.0)


@pytest.fixture
def uprior():
    return UniformPrior(lb=0.0, ub=1.0)


@pytest.fixture
def spline_specs():
    return SplineSpecs(knots=np.linspace(0.0, 1.0, 5),
                       degree=3,
                       knots_type="rel_domain")


@pytest.fixture
def spline_gprior():
    return SplineGaussianPrior(mean=0.0, sd=1.0, order=1)


@pytest.fixture
def spline_uprior():
    return SplineUniformPrior(lb=0.0, ub=np.inf, order=1)


@pytest.fixture
def var_cov0(gprior, uprior):
    return Variable(name="cov0",
                    priors=[gprior, uprior])


@pytest.fixture
def var_cov1(spline_gprior, spline_uprior, spline_specs):
    return SplineVariable(name="cov1",
                          spline_specs=spline_specs,
                          priors=[spline_gprior, spline_uprior])


@pytest.fixture
def param(var_cov0, var_cov1):
    return Parameter(name="mu",
                     variables=[var_cov0, var_cov1],
                     inv_link="exp")


def test_check_data(param, data):
    param.check_data(data)
    assert all([var.spline is not None
                for var in param.variables
                if isinstance(var, SplineVariable)])


def test_get_mat(param, data):
    param.check_data(data)
    mat = param.get_mat(data)
    assert mat.shape == (data.num_obs, param.size)


def test_get_uvec(param):
    uvec = param.get_uvec()
    assert uvec.shape == (2, param.size)


def test_get_gvec(param):
    gvec = param.get_gvec()
    assert gvec.shape == (2, param.size)


def test_get_linear_uvec(param, spline_uprior):
    uvec = param.get_linear_uvec()
    assert uvec.shape == (2, spline_uprior.size)


def test_get_linear_gvec(param, spline_gprior):
    gvec = param.get_linear_gvec()
    assert gvec.shape == (2, spline_gprior.size)


def test_get_linear_umat(param, data, spline_uprior):
    param.check_data(data)
    umat = param.get_linear_umat()
    assert umat.shape == (spline_uprior.size, param.size)


def test_get_linear_gmat(param, data, spline_gprior):
    param.check_data(data)
    gmat = param.get_linear_gmat()
    assert gmat.shape == (spline_gprior.size, param.size)


def test_get_lin_param(param, data):
    param.check_data(data)
    coefs = np.ones(param.size)
    mat = param.get_mat(data)
    lin_param1 = param.get_lin_param(coefs, data)
    lin_param2 = param.get_lin_param(coefs, data, mat=mat)
    assert np.allclose(lin_param1, lin_param2)


def test_get_param(param, data):
    param.check_data(data)
    coefs = np.ones(param.size)
    mat = param.get_mat(data)
    param1 = param.get_param(coefs, data)
    param2 = param.get_param(coefs, data, mat=mat)
    assert np.allclose(param1, param2)


def test_get_dparam(param, data):
    param.check_data(data)
    coefs = np.ones(param.size)
    mat = param.get_mat(data)
    dparam1 = param.get_dparam(coefs, data)
    dparam2 = param.get_dparam(coefs, data, mat=mat)
    assert np.allclose(dparam1, dparam2)


def test_get_d2param(param, data):
    param.check_data(data)
    coefs = np.ones(param.size)
    mat = param.get_mat(data)
    d2param1 = param.get_d2param(coefs, data)
    d2param2 = param.get_d2param(coefs, data, mat=mat)
    assert np.allclose(d2param1, d2param2)
