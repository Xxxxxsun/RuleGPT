# RuleGPT
This repository contains the implementation of RuleGPT from the paper **["HORAE: A Domain-Agnostic Modeling Language for Automating Multimodal Service Regulation"](https://arxiv.org/abs/2406.06600)**. It consists of two main components: firstly, we have open-sourced the RuleGPT model weights on Hugging Face, which can be quickly deployed using Docker images through the scripts provided in this repository. Secondly, we have also released the SRR-Eval <a href="https://huggingface.co/datasets/Xfgll/SRR-Eval">🤗</a> dataset on Hugging Face. This repository includes scripts for fine-tuning from the base **[Qwen-7B-Chat](https://github.com/QwenLM/Qwen/tree/main)**  model to obtain RuleGPT.

## Deploy RuleGPT with Docker🐳
To simplify the deployment process, we use docker image **[qwenllm/qwen](https://hub.docker.com/r/qwenllm/qwen)**
### Requirement
1. Install the correct version of Nvidia driver depending on the image to use:
- `qwenllm/qwen:cu117`: `>= 515.48.07`

2. Install and configure [docker](https://docs.docker.com/engine/install/) and [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html):

```bash
# configure docker
sudo systemctl start docker
# test if docker is correctly installed
sudo docker run hello-world

# configure nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
# test if nvidia-container-toolkit is correctly installed
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

3. Download RuleGPT model checkpoints to your environment.

### Deployment

Before launching a API, first you can setup the configuration:

```bash
IMAGE_NAME=qwenllm/qwen:cu117
PORT=8901
CHECKPOINT_PATH=/path/to/RuleGPT-logic   # Path to downloaded model checkpoints
```
The following script can help you build:

* OpenAI API
```bash
bash docker/docker_openai_api.sh -i ${IMAGE_NAME} -c ${CHECKPOINT_PATH} --port ${PORT}
```

The demo is successfully launched if you see the following output:

```text
Successfully started web demo. Open '...' to try!
Run `docker logs ...` to check demo status.
Run `docker rm -f ...` to stop and remove the demo.
```

If you want to check the status of the demo, you can use `docker logs qwen` to display outputs.

You can use `docker rm -f qwen` to stop the service and remove the container.

## Fine-tune RuleGPT with Docker🐳

We finetune Qwen-7B-Chat into RuleGPT using the pre-built Docker image in this repository. All the dependencies are already installed in the image:

Below is the script of finetuning process, we use single-GPU LoRA strategy:
```bash
IMAGE_NAME=qwenllm/qwen:cu117
CHECKPOINT_PATH=/path/to/Qwen-7B-Chat                # Path to downloaded original Qwen model checkpoints
DATA_PATH=/path/to/data/root                    # Prepare finetune data at ${DATA_PATH}/example.json
OUTPUT_PATH=/path/to/output/checkpoint          # Path to finetune outputs

# Use all host devices by default
DEVICE=all
# If you need to specify GPUs for training, set device as follow (NOTE: internal quotation marks cannot be omitted)
#DEVICE='"device=0,1,2,3"'

mkdir -p ${OUTPUT_PATH}

# Single-GPU LoRA finetuning
docker run --gpus ${DEVICE} --rm --name qwen \
    --mount type=bind,source=${CHECKPOINT_PATH},target=/data/shared/Qwen/Qwen-7B \
    --mount type=bind,source=${DATA_PATH},target=/data/shared/Qwen/data \
    --mount type=bind,source=${OUTPUT_PATH},target=/data/shared/Qwen/output_qwen \
    --shm-size=2gb \
    -it ${IMAGE_NAME} \
    bash finetune/finetune_lora_single_gpu.sh -m /data/shared/Qwen/Qwen-7B/ -d /data/shared/Qwen/data/example.json
```

<br>
