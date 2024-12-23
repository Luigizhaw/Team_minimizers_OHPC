import numpy as np
import matplotlib.pyplot as plt

def solar_cycle_model(t, params):
    """
    Calculate the solar cycle model values.

    Parameters:
    - t: array-like, time points.
    - params: array-like, parameters [T0_1, Ts_1, Td_1, ..., T0_n, Ts_n, Td_n].

    Returns:
    - model_values: array-like, calculated model values at time t.
    """
    n_cycles = len(params) // 3
    T0 = params[::3]
    epsilon = 1e-5  # Avoid division by zero
    Ts = np.clip(params[1::3], epsilon, None)
    Td = np.clip(params[2::3], epsilon, None)

    t = np.atleast_1d(t)
    result = np.zeros_like(t)
    intervals = [(T0[i], T0[i + 1]) for i in range(n_cycles - 1)] + [(T0[-1], np.inf)]

    for i, (a, b) in enumerate(intervals):
        mask = (a <= t) & (t < b)
        exponent = -((t[mask] - T0[i]) / Td[i]) ** 2
        exponent = np.clip(exponent, -100, 0)
        result[mask] = (((t[mask] - T0[i]) / Ts[i]) ** 2) * np.exp(exponent)

    return result

def mse_loss(params, t_obs, y_obs, regularization=1e-3):
    """
    Calculate the MSE loss with regularization.

    Parameters:
    - params: array-like, model parameters.
    - t_obs: array-like, observed time points.
    - y_obs: array-like, observed sunspot numbers.
    - regularization: float, penalty for parameter magnitude.

    Returns:
    - mse: float, the MSE loss.
    """
    y_pred = solar_cycle_model(t_obs, params)
    mse = np.mean((y_obs - y_pred) ** 2)
    reg_term = regularization * np.sum(params ** 2)
    return mse + reg_term

def simulated_annealing_tuning(x0, T0, sigma, f, n_iter=1000, thinning=1, early_stop_threshold=1e-6):
    """
    Perform simulated annealing to optimize parameters.

    Parameters:
    - x0: Initial parameter values (array-like).
    - T0: Initial temperature.
    - sigma: Standard deviation for parameter jumps.
    - f: Loss function to minimize.
    - n_iter: Number of iterations.
    - thinning: Save states at regular intervals.
    - early_stop_threshold: float, threshold for early stopping.

    Returns:
    - v: Array of parameter values across iterations.
    """
    x = x0.copy()
    T = T0
    n_params = x0.shape[0]
    means = np.zeros(n_params)
    cov_matrix = np.diag(np.full(n_params, sigma))

    size_out = int((n_iter + thinning - 1) // thinning)
    v = np.zeros((size_out, n_params))
    v[0, :] = x

    iter_counter = 0
    iter_counter_thin = 0
    best_loss = f(x)
    best_params = x.copy()
    print(f"Initial loss: {best_loss}")

    no_improvement_count = 0
    sigma_decay_rate = 0.99  # Adaptive sigma decay rate

    while iter_counter < n_iter:
        iter_counter += 1
        x_old = x
        x_proposal = x_old + np.random.multivariate_normal(means, cov_matrix)
        DeltaE = f(x_proposal) - f(x_old)

        if np.exp(-np.clip(DeltaE / T, -100, 100)) >= np.random.rand():
            x = x_proposal
            current_loss = f(x)
            if current_loss < best_loss:
                best_loss = current_loss
                best_params = x.copy()
                no_improvement_count = 0
            else:
                no_improvement_count += 1

        T *= 0.98  #0.995  # Cooling schedule
        sigma *= sigma_decay_rate  # Adjust step size dynamically

        if iter_counter % thinning == 0:
            v[iter_counter_thin, :] = x
            iter_counter_thin += 1

        if iter_counter % 100 == 0: # changed fromm 1e3
            print(f"Iteration {iter_counter}: Loss = {best_loss}")

        if no_improvement_count > 500:
            print(f"Early stopping at iteration {iter_counter}: Loss = {best_loss}")
            break

    print(f"Best loss: {best_loss} | Parameters: {best_params}")
    return v

def optimize_solar_model(t_obs, y_obs, x0, T0, sigma, n_iter=1e5, early_stop_threshold=1e-6):
    """
    Optimize the solar cycle model parameters using simulated annealing.

    Parameters:
    - t_obs: array-like, observed time points.
    - y_obs: array-like, observed sunspot numbers.
    - x0: array-like, initial parameters.
    - T0: float, initial temperature.
    - sigma: float, standard deviation for parameter jumps.
    - n_iter: int, number of iterations.
    - early_stop_threshold: float, threshold for early stopping.

    Returns:
    - best_params: array-like, optimized parameters.
    """
    def loss_function(x):
        return mse_loss(x, t_obs, y_obs, regularization=1e-3)

    return simulated_annealing_tuning(x0, T0, sigma, loss_function, n_iter=n_iter, early_stop_threshold=early_stop_threshold)

def plot_solar_model(t_obs, y_obs, params):
    """
    Plot the observed vs. modeled data.

    Parameters:
    - t_obs: array-like, observed time points.
    - y_obs: array-like, observed sunspot numbers.
    - params: array-like, optimized parameters.
    """
    y_pred = solar_cycle_model(t_obs, params)

    plt.figure(figsize=(10, 6))
    plt.scatter(t_obs, y_obs, label="Observed Data", color="orange", s=10)
    plt.plot(t_obs, y_pred, label="Model Fit", color="blue", linewidth=2)
    plt.xlabel("Time")
    plt.ylabel("Sunspot Number")
    plt.title("Solar Cycle Model Fit")
    plt.legend()
    plt.grid(True)
    plt.show()
