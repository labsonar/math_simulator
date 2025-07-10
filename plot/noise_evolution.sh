#!/bin/bash

# python plot/noise_evolution.py --export-trajectories
# python plot/noise_evolution.py --export-trajectories-tex

# python plot/noise_evolution.py --run_speed_test
# python plot/noise_evolution.py --run_blade_test

# python plot/noise_evolution.py --each-ship-signal

# python plot/noise_evolution.py --export-complete
# python plot/noise_evolution.py --export-complete --with-environment

# python plot/noise_evolution.py --export-complete --with-environment --step-duration 10 --n-steps 4
# python plot/noise_evolution.py --export-complete --with-environment --step-duration 5 --n-steps 8
# python plot/noise_evolution.py --export-complete --with-environment --step-duration 0.5 --n-steps 80
# python plot/noise_evolution.py --export-complete --with-environment --step-duration 0.1 --n-steps 400
# python plot/noise_evolution.py --export-complete --with-environment --step-duration 0.01 --n-steps 4000

# python plot/noise_evolution.py --run_channel_test --with-environment

# python plot/noise_evolution.py --both-ship-signals --with-environment --vary-depth
# python plot/noise_evolution.py --both-ship-signals --with-environment --vary-seabed

# python plot/noise_evolution.py --run_ss_test --with-environment
python plot/noise_evolution.py --run_depth_test --with-environment

# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/blade_test/bulker --n_fft 1024 --max_freq 40 --merge
# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/blade_test/bulker --n_fft 1024 --max_freq 40 --merge --export_tex
# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/blade_test/fishing --n_fft 1024 --max_freq 160 --merge
# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/blade_test/fishing --n_fft 1024 --max_freq 160 --merge --export_tex

# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/speed_test/bulker --n_fft 1024 --max_freq 40 --merge
# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/speed_test/bulker --n_fft 1024 --max_freq 40 --merge --export_tex
# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/speed_test/fishing --n_fft 1024 --max_freq 160 --merge
# python lps_libraries/signal_processing/apps/demon.py ./result/noise_evolution/speed_test/fishing --n_fft 1024 --max_freq 160 --merge --export_tex

# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/channel_resolution --integration_time 1 --integration_overlap 0.5
# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/channel_resolution --integration_time 1 --integration_overlap 0.5 --export_tex

# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/seabed_test --integration_time 1 --integration_overlap 0.5
# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/seabed_test --integration_time 1 --integration_overlap 0.5 --export_tex

# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/complete --integration_time 1 --integration_overlap 0.5
# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/complete --integration_time 1 --integration_overlap 0.5 --export_tex

# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/ss_test --integration_time 1 --integration_overlap 0.5
# python lps_libraries/signal_processing/apps/spectral_analysis.py ./result/noise_evolution/ss_test --integration_time 1 --integration_overlap 0.5 --export_tex
