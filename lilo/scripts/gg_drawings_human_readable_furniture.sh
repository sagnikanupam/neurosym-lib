python run_iterative_experiment.py --experiment_name gg_drawings_human_readable --domain drawings_furniture --experiment_type stitch --stitch_params '{"iterations": 10}' --random_seeds 111 
python run_iterative_experiment.py --experiment_name gg_drawings_human_readable --domain drawings_furniture --experiment_type oracle --stitch_params '{"iterations": 10}' --random_seeds 111 
python run_iterative_experiment.py --experiment_name gg_drawings_human_readable --domain drawings_furniture --experiment_type oracle_train_test --stitch_params '{"iterations": 10}' --random_seeds 111 
python run_iterative_experiment.py --experiment_name gg_drawings_human_readable --domain drawings_furniture --experiment_type stitch_codex --stitch_params '{"iterations": 10}' --codex_params '{"n_tasks_per_prompt": 25, "n_samples": 50, "n_samples_per_query": 5, "final_task_origin": "default", "body_task_types": ["programs"], "final_task_types": ["programs"], "function_name_classes": ["human_readable"]}' --use_cached --random_seeds 111 222 333 
python run_iterative_experiment.py --experiment_name gg_drawings_human_readable --domain drawings_furniture --experiment_type stitch_codex_language --stitch_params '{"iterations": 10}' --codex_params '{"n_tasks_per_prompt": 25, "n_samples": 50, "n_samples_per_query": 5, "final_task_origin": "default", "body_task_types": ["language", "programs"], "final_task_types": ["language"], "function_name_classes": ["human_readable"]}' --use_cached --random_seeds 111 222 333 
python run_iterative_experiment.py --experiment_name gg_drawings_human_readable --domain drawings_furniture --experiment_type stitch_codex_language_origin_random_test --stitch_params '{"iterations": 10}' --codex_params '{"n_tasks_per_prompt": 25, "n_samples": 50, "n_samples_per_query": 5, "final_task_origin": "default", "body_task_types": ["language", "programs"], "final_task_types": ["language"], "function_name_classes": ["human_readable"]}' --use_cached --random_seeds 111 222 333 
