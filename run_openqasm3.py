"""Helper methods for running OpenQASM3 programs.

(C) Copyright IBM 2021.

"""

from typing import List, Union

from qiskit import QuantumCircuit

from qiskit.providers.ibmq import IBMQJob, IBMQBackend, RunnerResult

QASM3_INPUT = Union[QuantumCircuit, str]

def run_openqasm3(circuits: Union[QASM3_INPUT, List[QASM3_INPUT]], backend: IBMQBackend, verbose: bool = True, draw: bool = True) -> List[IBMQJob]:
    """Run an OpenQASM3 job through the circuit runner.

    Args:
        circuits: A single(list) of :class:`qiskit.QuantumCircuit` or QASM3 source strings to be run.
        backend: Target backend to run on.
        verbose: Verbose execution mode.
        draw: Draw the circuit as part of verbose mode. Note: Cannot draw QASM3 source string.
    """

    if isinstance(circuits, (QuantumCircuit, str)):
        circuits = [circuits]

    config = backend.configuration()
    provider = backend.provider()

    for circuit_idx, circuit in enumerate(circuits):
        if verbose:
            if isinstance(circuit, QuantumCircuit):
                print(f"======{circuit.name}======")
                try:
                    from qiskit import qasm3
                    print("=======QASM3======")
                    print(qasm3.Exporter(includes=[], basis_gates=config.basis_gates).dumps(circuit))
                except ImportError:
                    print('The QASM3 exporter is unavailable. Please install the "main" branch of Qiskit.')

                print("==================")
                if draw:
                    print(circuit.draw())
                    print("==================")
            else:
                print("==================")
                print(circuit)
                print("==================")

    runtime_params = {
        'circuits': circuits,
        'exporter_config': {
            "disable_constants": True
        }
    }

    options = {'backend_name': backend.name()}

    job = provider.runtime.run(
        program_id="qasm3-runner",
        options=options,
        inputs=runtime_params,
        result_decoder=RunnerResult,
        image="qiskit-program-qasm3:latest"
    )
    if verbose:
        print(f"Running: {job.job_id()}")

    if verbose:
        result = job.result()
        for circuit_idx, circuit in enumerate(circuits):
            counts = result.get_counts(circuit_idx)
            if isinstance(circuit, QuantumCircuit):
                print(f"======={circuit.name}=======")
            print (counts)

    return job
