****************
itteration_tools
****************


SimpleSingleParamOptimiser
==========================

Here is a example of how the SimpleSingleParamOptimiser class could be used
with the surrouding code to support this.

Setting up initial files
------------------------

First this code makes an initial batch of Sonnet files that will be used as the
base of the optimser and will be the files itterated upon to achieve the
desired result.

.. code-block:: python

    #file - example.py
    from sonnetsuiteshelper import file_generation

    print("Making the initial Batch 1")
    base_file_to_edit_name = "file_to_edit.son"
    base_file_to_edit_path = "base_file_for_generate"

    output_folder = "batch_1_made_files"

    lens_to_use = [1100.0, 1275.0, 1450.0, 1625.0, 1800.0, 1975.0]

    for file_no, len in enumerate(lens_to_use):
        params_to_edit_dict = {}
        params_to_edit_dict["length_var"] = len

        name_for_output_file = f"V1__file_({file_no})_len_{len}.son"

        file_generation.generate_file_like(
            base_filename=base_file_to_edit_name,
            base_file_path=base_file_to_edit_path,
            output_filename=name_for_output_file,
            output_file_path=output_folder,
            params_to_edit=params_to_edit_dict,
        )
    print("made all initial files")

The file structure after this has been run looks like: ::

    example_folder
    ├── batch_1_made_files
    │   ├── V1__file_(0)_len_1100.0.son
    │   ├── V1__file_(1)_len_1275.0.son
    │   ├── V1__file_(2)_len_1450.0.son
    │   ├── V1__file_(3)_len_1625.0.son
    │   ├── V1__file_(4)_len_1800.0.son
    │   └── V1__file_(5)_len_1975.0.son
    └── example.py

Now these files can be analysed in Sonnet.

Setting up SimpleSingleParamOptimiser
-------------------------------------

The output csv from these son files analysed has for this next example have
been placed in a folder called "batch_1_outputs". However if they still exist
in the same directory as the son file then be sure to change the
batch_1_output_file_path variable to "batch_1_made_files" in the snippet below.

The next code will set up an optimiser for those Sonnet files.

.. code-block:: python

    #file - example.py
    from sonnetsuiteshelper import itteration_tools

    print("Making optimiser objects")

    dict_of_optimizations = {}

    varaible_param_name = "length_var"
    desired_output_param = "QR"
    desired_output_param_value = 10000.0
    desired_output_param_value_tolerence_percent = 0.010
    correlation = "-"

    for file_no, len in enumerate(lens_to_use):
        batch_1_son_filename = f"V1__file_({file_no})_len_{len}.son"
        batch_1_son_file_path = "batch_1_made_files"

        batch_1_output_filename = f"V1__file_({file_no})_len_{len}.csv"
        batch_1_output_file_path = "batch_1_outputs"

        init_variable_param_value = len

        optimiser_name = f"{file_no}_{len}"

        optimiser_object = itteration_tools.SimpleSingleParamOptimiser(
            optimiser_name,
            varaible_param_name,
            batch_1_son_filename,
            batch_1_son_file_path,
            batch_1_output_filename,
            batch_1_output_file_path,
            init_variable_param_value,
            desired_output_param,
            desired_output_param_value,
            desired_output_param_value_tolerence_percent,
            correlation,
            sonnet_mesh_size=1.0,
            ignore_loading_cache=False,
        )

        dict_of_optimisations[optimiser_name] = optimiser_object

Note that these optimisers objects have been loaded into a dict such that
itterating through them all is a bit easier as shown by the next example.

By making an optimiser object, it will automatically analyse that first output
file and make the next batch of files.

The file structure after this has been run looks like: ::

    example_folder
    ├── batch_1_made_files
    │   ├── V1__file_(0)_len_1100.0.son
    │   ├── V1__file_(1)_len_1275.0.son
    │   ├── V1__file_(2)_len_1450.0.son
    │   ├── V1__file_(3)_len_1625.0.son
    │   ├── V1__file_(4)_len_1800.0.son
    │   └── V1__file_(5)_len_1975.0.son
    ├── batch_1_outputs
    │   ├── V1__file_(0)_len_1100.0.csv
    │   ├── V1__file_(1)_len_1275.0.csv
    │   ├── V1__file_(2)_len_1450.0.csv
    │   ├── V1__file_(3)_len_1625.0.csv
    │   ├── V1__file_(4)_len_1800.0.csv
    │   └── V1__file_(5)_len_1975.0.csv
    ├── batch_2_generated_files
    │   ├── batch_2__0_1100.0_length_var_1150.0.son
    │   ├── batch_2__1_1275.0_length_var_1325.0.son
    │   ├── batch_2__2_1450.0_length_var_1500.0.son
    │   ├── batch_2__3_1625.0_length_var_1675.0.son
    │   ├── batch_2__4_1800.0_length_var_1850.0.son
    │   └── batch_2__5_1975.0_length_var_2025.0.son
    ├── OptCache
    │   ├── SSPOC_0_1100.0.yml
    │   ├── SSPOC_1_1275.0.yml
    │   ├── SSPOC_2_1450.0.yml
    │   ├── SSPOC_3_1625.0.yml
    │   ├── SSPOC_4_1800.0.yml
    │   └── SSPOC_5_1975.0.yml
    └── example.py

Itterating using SimpleSingleParamOptimiser
-------------------------------------------

Once these next output files have been analysed with Sonnet and csv output made,
the next snippet will itterate through all the optimisers and generate the next
batch of files.

.. code-block:: python

    #file - example.py
    for optimiser_name, optimiser_obj in dict_of_optimisations.items():
        next_batch_output_exists = True

        while next_batch_output_exists:
            filename = optimiser_obj.get_last_analysis_filename()
            file_path = optimiser_obj.get_last_analysis_file_path()
            if not os.path.isfile(os.path.join(file_path, filename)):
                print("Sonnet output file does not exist")
                next_batch_output_exists = False
                break

            optimiser_obj.analyze_batch()
            optimiser_obj.generate_next_batch()

This code runs through each optimiser_object in the dictionary containing all
the optimiser_objects. Then for that optimiser_obj, if the analysis file it
expects to find exists then it will analyse that batch and generate the next
batch. This continues untill it cannot find an analysis file then it breaks and
moves on to the next optimiser_obj.

This structure of code takes full advantage of the caching that happens in the
optimiser object where is updates it state to a cache file after each
generate_next_batch() call. This means that if this code is rerun it will only
analyse the last batch and not every batch leading up to and including that
eliminating the overhead of making lots of files already made.

The file structure after this has been run looks like: ::

    example_folder
    ├── batch_1_made_files
    │   ├── V1__file_(0)_len_1100.0.son
    │   ├── V1__file_(1)_len_1275.0.son
    │   ├── V1__file_(2)_len_1450.0.son
    │   ├── V1__file_(3)_len_1625.0.son
    │   ├── V1__file_(4)_len_1800.0.son
    │   └── V1__file_(5)_len_1975.0.son
    ├── batch_1_outputs
    │   ├── V1__file_(0)_len_1100.0.csv
    │   ├── V1__file_(1)_len_1275.0.csv
    │   ├── V1__file_(2)_len_1450.0.csv
    │   ├── V1__file_(3)_len_1625.0.csv
    │   ├── V1__file_(4)_len_1800.0.csv
    │   └── V1__file_(5)_len_1975.0.csv
    ├── batch_2_generated_files
    │   ├── batch_2__0_1100.0_length_var_1150.0.son
    │   ├── batch_2__1_1275.0_length_var_1325.0.son
    │   ├── batch_2__2_1450.0_length_var_1500.0.son
    │   ├── batch_2__3_1625.0_length_var_1675.0.son
    │   ├── batch_2__4_1800.0_length_var_1850.0.son
    │   └── batch_2__5_1975.0_length_var_2025.0.son
    ├── batch_2_outputs
    │   ├── batch_2__0_1100.0_length_var_1150.0.csv
    │   ├── batch_2__1_1275.0_length_var_1325.0.csv
    │   ├── batch_2__2_1450.0_length_var_1500.0.csv
    │   ├── batch_2__3_1625.0_length_var_1675.0.csv
    │   ├── batch_2__4_1800.0_length_var_1850.0.csv
    │   └── batch_2__5_1975.0_length_var_2025.0.csv
    ├── batch_2_generated_files
    │   ├── batch_2__0_1100.0_length_var_1175.0.son
    │   ├── batch_2__1_1275.0_length_var_1350.0.son
    │   ├── batch_2__2_1450.0_length_var_1525.0.son
    │   ├── batch_2__3_1625.0_length_var_1700.0.son
    │   ├── batch_2__4_1800.0_length_var_1875.0.son
    │   └── batch_2__5_1975.0_length_var_2050.0.son
    ├── batch_2_outputs
    │   ├── batch_2__0_1100.0_length_var_1175.0.csv
    │   ├── batch_2__1_1275.0_length_var_1350.0.csv
    │   ├── batch_2__2_1450.0_length_var_1525.0.csv
    │   ├── batch_2__3_1625.0_length_var_1700.0.csv
    │   ├── batch_2__4_1800.0_length_var_1875.0.csv
    │   └── batch_2__5_1975.0_length_var_2050.0.csv
    ├── batch_3_generated_files
    │   └── ...
    ├── batch_3_outputs
    │   └── ...
    ├── batch_4_generated_files
    │   └── ...
    ├── batch_4_outputs
    │   └── ...
    ├── OptCache
    │   ├── SSPOC_0_1100.0.yml
    │   ├── SSPOC_1_1275.0.yml
    │   ├── SSPOC_2_1450.0.yml
    │   ├── SSPOC_3_1625.0.yml
    │   ├── SSPOC_4_1800.0.yml
    │   └── SSPOC_5_1975.0.yml
    └── example.py

Once those files have been again analysed in Sonnet and csv outputs made that
same code will generate every next batch untill the optimsations have finished.

Plotting SimpleSingleParamOptimiser output
------------------------------------------

This next snippet utilises the plotting functions built into the optimiser
object to show the current state of the optimiser.

.. code-block:: python

    #file - example.py
    for optimiser_name, optimiser_obj in dict_of_optimisations.items():
        optimiser_object.plot_optimisation()

This next snippet utilises the plotting functions but supplies a matplotlib
figure axes to create a custom plot showing all the current optimisers state's
in one figure opposed to one seperate figure for each. This means any
matplotlib plot setup can be used to and customised to best suit the
application and make it clear whats happening.

.. code-block:: python

    #file - example.py

    title = "all_plotted"
    fig = plt.figure(title)
    plt.clf()
    rows = 2
    cols = 3
    grid = plt.GridSpec(rows, cols)

    ax_dict = {}
    for row in range(rows):
        for col in range(cols):
            ax_dict[f"{row}_{col}"] = plt.subplot(grid[row, col])

    file_no_to_ax = {
        0: "0_0"
        1: "0_1"
        2: "0_2"
        3: "1_0"
        4: "1_1"
        5: "1_2"
    }

    for file_no, (opt_name, opt_obj) in enumerate(dict_of_optimizations.items()):
        ax_name = file_no_to_ax[file_no]
        ax = ax_dict[ax_name]

        optimizer.plot_optimisation(
            fig_ax=ax,
            plot_fit_function=True,
            plot_next_batch_variable_value=True,
            set_axis_labels=False,
        )

        ax.set_title(f"file_no - {file_no}")

    ax_dict["0_0"].set_ylabel("QR")
    ax_dict["1_0"].set_ylabel("QR")

    ax_dict["0_0"].set_xlabel("length_var")
    ax_dict["0_0"].set_xlabel("length_var")
    ax_dict["1_0"].set_xlabel("length_var")

    fig.suptitle("All Optimisations")
    fig.show()
